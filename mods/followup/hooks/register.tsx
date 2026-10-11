import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { FollowupQueue } from '../types'

const queue = atom({ plugin: 'followup', key: 'queue' } as const, [] as FollowupQueue)
const isPaused = atom({ plugin: 'followup', key: 'isPaused' } as const, false)
const isBusy = atom({ plugin: 'followup', key: 'isBusy' } as const, false)

// Agent loops that are still working; a follow-up waits for them too.
const LIVE_AGENT = new Set(['pending', 'running', 'waiting'])
const BAND_ROWS = 3
const DISPATCH_DELAY_MS = 50

const preview = (text: string, max = 80) => {
  const line = (text.split('\n')[0] ?? '').trim()
  return line.length > max ? `${line.slice(0, max - 1)}…` : line
}

const plural = (n: number) => `${n} follow-up${n === 1 ? '' : 's'}`

const hasLiveAgents = async ($: EngineInterface) => {
  try {
    const agents = await $.agent.list()
    return agents.some(agent => LIVE_AGENT.has(agent.status))
  } catch {
    return false
  }
}

// Sends the head of the queue as a turn of its own, once nothing is running.
const dispatchNext = async ($: EngineInterface) => {
  if ((await read($, isPaused)) || (await read($, isBusy))) return
  const list = await read($, queue)
  if (list.length === 0) return
  if (await hasLiveAgents($)) {
    $.ui.status(`${plural(list.length)} waiting on background agents`)
    return
  }
  $.ui.status(undefined)

  // Pop inside update so an item queued meanwhile is never overwritten.
  let text: string | undefined
  await update($, queue, l => {
    text = l[0]
    return l.slice(1)
  })
  if (text === undefined) return
  // Claim the session now so a second turn.complete cannot send twice.
  await update($, isBusy, () => true)

  // Never awaited: inside a hook the session is not idle yet, and the
  // submission resolves only once its own turn starts.
  const sent = text
  void $.prompt.submit({ text: sent, asUser: true }).then(
    async result => {
      if (result.drop !== undefined) await update($, isBusy, () => false)
    },
    async () => {
      await update($, queue, l => [sent, ...l])
      await update($, isBusy, () => false)
      $.ui.toast('Follow-up could not be sent; it is back at the head of the queue')
    },
  ).catch(() => undefined) // the session (or a test) may be gone by now
}

// The engine refuses $.prompt.submit inside a command or press hook (it would
// wait on the hook holding the session), so those paths go through a timer.
const dispatchSoon = ($: EngineInterface) => {
  $.clock.after(DISPATCH_DELAY_MS, () => void dispatchNext($).catch(() => undefined))
}

// A dropped prompt stays in the box as the draft. Once the drop has landed,
// empty it, but only while it still holds what was queued.
const clearQueuedDraft = ($: EngineInterface, text: string) => {
  $.clock.after(DISPATCH_DELAY_MS, async () => {
    try {
      const box = await $.prompt.read()
      if (box.text.trim() === text) await $.prompt.fill({ text: '', mode: 'replace' })
    } catch {
      // no box, or a dialog holds it; the draft simply stays
    }
  })
}

const enqueue = async ($: EngineInterface, text: string) => {
  const list = await update($, queue, l => [...l, text])
  return list.length
}

const listing = (list: FollowupQueue, paused: boolean) => {
  if (list.length === 0) return 'No follow-ups queued.'
  const head = `${plural(list.length)} queued${paused ? ' (paused)' : ''}:`
  return [head, ...list.map((t, i) => `  ${i + 1}. ${preview(t, 120)}`)].join('\n')
}

const HELP = [
  '/later <prompt>  queue a prompt to run after the agent fully finishes',
  '/later           list the queue',
  '/later run       resume and send the next one when idle',
  '/later pause     hold the queue',
  '/later drop [n]  remove item n (default: the last)',
  '/later clear     empty the queue',
  'ctrl+x enter during a turn queues what you typed as a follow-up.',
].join('\n')

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'later',
      description: 'Queue a follow-up prompt for when the agent is fully done',
      argumentHint: '[prompt | run | pause | drop [n] | clear | help]',
      immediate: true,
    })
    return next(e)
  })

  // ctrl+x enter (chat:queueSubmit) during a turn: hold it as a follow-up
  // instead of letting the engine fold it into the running turn.
  on('prompt.submit', async ($, e, next) => {
    const isQueueKey = e.wait && e.turnId !== undefined && e.origin.kind === 'composer'
    const text = e.text.trim()
    if (!isQueueKey || text === '' || (e.attachments?.length ?? 0) > 0) return next(e)

    const n = await enqueue($, text)
    $.ui.toast(`Queued as follow-up #${n}`)
    clearQueuedDraft($, text)
    return { drop: `Queued as follow-up #${n}; it runs when the agent is done.` }
  })

  on('turn.start', async ($, e, next) => {
    await update($, isBusy, () => true)
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId !== undefined) return result

    await update($, isBusy, () => false)
    const waiting = (await read($, queue)).length
    if (waiting === 0) return result

    if (e.reason !== 'answer') {
      await update($, isPaused, () => true)
      $.ui.toast(`Turn ended (${e.reason}); ${plural(waiting)} paused. /later run to resume.`)
      return result
    }

    await dispatchNext($)
    return result
  })

  on('command.run', { command: 'later' }, async ($, e) => {
    const args = e.args.trim()
    const [verb = '', ...rest] = args.split(/\s+/)

    if (args === '') {
      return { text: listing(await read($, queue), await read($, isPaused)) }
    }
    if (args === 'help') return { text: HELP }
    if (args === 'clear') {
      await update($, queue, () => [])
      await update($, isPaused, () => false)
      $.ui.status(undefined)
      return { text: 'Follow-up queue cleared.' }
    }
    if (args === 'pause') {
      await update($, isPaused, () => true)
      return { text: 'Follow-ups paused. /later run to resume.' }
    }
    if (args === 'run' || args === 'resume') {
      await update($, isPaused, () => false)
      const n = (await read($, queue)).length
      dispatchSoon($)
      return { text: n === 0 ? 'Nothing queued.' : `Resumed; ${plural(n)} queued.` }
    }
    if (verb.toLowerCase() === 'drop' && rest.length <= 1 && rest.every(n => /^\d+$/.test(n))) {
      const list = await read($, queue)
      if (list.length === 0) return { text: 'Nothing queued.' }
      const index = rest[0] === undefined ? list.length - 1 : Number(rest[0]) - 1
      if (index < 0 || index >= list.length) return { text: `No follow-up #${index + 1}.` }
      await update($, queue, l => l.filter((_, i) => i !== index))
      return { text: `Dropped follow-up #${index + 1}: ${preview(list[index] ?? '')}` }
    }

    const n = await enqueue($, args)
    const isIdle = !(await read($, isBusy)) && !(await read($, isPaused))
    if (isIdle) dispatchSoon($)
    return { text: isIdle ? 'Agent idle; sending it now.' : `Queued as follow-up #${n}.` }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const list = await read($, queue)
    if (e.props.hasSurvey || list.length === 0) return next(e)

    const paused = await read($, isPaused)
    const { Box, Button, Text } = $.ui.resolve(e)
    const width = Math.max(20, e.props.bodyColumns - 6)
    const state = paused ? 'paused' : e.props.isWorking ? 'after this turn' : 'next up'

    return (
      <Box flexDirection="column">
        <Box flexDirection="row" gap={1}>
          <Text color={paused ? 'warning' : 'suggestion'}>
            ⏳ {plural(list.length)} · {state}
          </Text>
          {paused ? (
            <Button key="resume" label="Resume" onPress={async () => {
              await update($, isPaused, () => false)
              dispatchSoon($)
            }} />
          ) : (
            <Button key="pause" label="Pause" onPress={() => update($, isPaused, () => true)} />
          )}
          <Button key="clear" label="Clear" onPress={async () => {
            await update($, queue, () => [])
            await update($, isPaused, () => false)
          }} />
        </Box>
        {list.slice(0, BAND_ROWS).map((t, i) => (
          <Text key={`item-${i}`} dimColor wrap="truncate-end">
            {'  '}{i + 1}. {preview(t, width)}
          </Text>
        ))}
        {list.length > BAND_ROWS && (
          <Text dimColor>  … {list.length - BAND_ROWS} more (/later to list)</Text>
        )}
      </Box>
    )
  })
}
