import { expect, mock, test } from 'claude-code/testing'
import type { AgentInfo, On, PromptSubmitInput, RenderElement } from 'claude-code'

const composer = { kind: 'composer' } as const

// The world beneath the plugin: records what reached the engine.
const world = (on: On, agents: AgentInfo[] = []) => {
  const submitted: PromptSubmitInput[] = []
  on('prompt.submit', ($, e) => {
    submitted.push(e)
    return { text: e.text }
  })
  on('turn.start', ($, e) => ({ turnId: e.turnId }))
  on('turn.complete', ($, e) => ({ text: e.answer }))
  on('agent.list', () => ({ value: agents }))
  on('ui.toast', () => ({ value: undefined }))
  on('ui.status', () => ({ value: undefined }))
  const clock = mock.clock(on)
  return { submitted, agents, clock }
}

const typed = (text: string, wait: boolean, turnId?: string): PromptSubmitInput => ({
  text,
  wait,
  origin: composer,
  ...(turnId === undefined ? {} : { turnId }),
})

const later = (args: string) => ({
  command: 'later',
  args,
  origin: composer,
  presentation: { isFullscreen: false, columns: 120 },
})

const done = (reason: 'answer' | 'aborted' = 'answer', agentId?: string) => ({
  answer: 'ok',
  durationMs: 1,
  isAborted: reason === 'aborted',
  turnId: 't1',
  reason,
  ...(agentId === undefined ? {} : { agentId }),
})

test('ctrl+x enter mid-turn is held, then sent after the turn ends', async ($, on) => {
  const { submitted } = world(on)
  await $.turn.start({ text: 'work', turnId: 't1' })

  const held = await $.prompt.submit(typed('run the tests', true, 't1'))
  expect(held.drop).toBeDefined()
  expect(submitted).toHaveLength(0)

  await $.turn.complete(done())
  expect(submitted.map(s => s.text)).toEqual(['run the tests'])
  expect(submitted[0]?.origin).toEqual({ kind: 'plugin', name: 'followup', asUser: true })
})

// The prompt box beneath the plugin: holds the draft, records fills.
const box = (on: On, draft: string) => {
  const state = { text: draft }
  on('prompt.read', () => ({ value: { text: state.text, cursor: state.text.length } }))
  on('prompt.fill', ($, e) => {
    state.text = e.mode === 'replace' ? e.text : state.text + e.text
    return { isFilled: true, text: state.text, cursor: state.text.length }
  })
  return state
}

test('ctrl+x enter empties the prompt box once queued', async ($, on) => {
  const { clock } = world(on)
  const draft = box(on, 'run the tests ')
  await $.turn.start({ text: 'work', turnId: 't1' })
  await $.prompt.submit(typed('run the tests ', true, 't1'))
  await clock.advance(100)
  expect(draft.text).toBe('')
})

test('a draft typed after queueing is left alone', async ($, on) => {
  const { clock } = world(on)
  const draft = box(on, 'run the tests')
  await $.turn.start({ text: 'work', turnId: 't1' })
  await $.prompt.submit(typed('run the tests', true, 't1'))
  draft.text = 'something new'
  await clock.advance(100)
  expect(draft.text).toBe('something new')
})

test('a plain Enter mid-turn still steers the running turn', async ($, on) => {
  const { submitted } = world(on)
  await $.turn.start({ text: 'work', turnId: 't1' })
  await $.prompt.submit(typed('also check lint', false, 't1'))
  expect(submitted.map(s => s.text)).toEqual(['also check lint'])
})

test('one follow-up per finished turn, in order', async ($, on) => {
  const { submitted } = world(on)
  await $.turn.start({ text: 'work', turnId: 't1' })
  await $.prompt.submit(typed('first', true, 't1'))
  await $.prompt.submit(typed('second', true, 't1'))

  await $.turn.complete(done())
  expect(submitted.map(s => s.text)).toEqual(['first'])
  // A second completion while the follow-up's turn has not started sends nothing.
  await $.turn.complete(done('answer', 'sub-1'))
  expect(submitted).toHaveLength(1)

  await $.turn.start({ text: 'first', turnId: 't2' })
  await $.turn.complete(done())
  expect(submitted.map(s => s.text)).toEqual(['first', 'second'])
})

test('an interrupted turn pauses the queue until /later run', async ($, on) => {
  const { submitted, clock } = world(on)
  await $.turn.start({ text: 'work', turnId: 't1' })
  await $.prompt.submit(typed('deploy', true, 't1'))

  await $.turn.complete(done('aborted'))
  expect(submitted).toHaveLength(0)

  await $.command.run(later('run'))
  await clock.advance(100)
  expect(submitted.map(s => s.text)).toEqual(['deploy'])
})

test('waits while a background agent is still running', async ($, on) => {
  const agent: AgentInfo = { id: 'a1', description: 'scan', type: 'Explore', status: 'running' }
  const { submitted, agents } = world(on, [agent])
  await $.turn.start({ text: 'work', turnId: 't1' })
  await $.prompt.submit(typed('summarize', true, 't1'))

  await $.turn.complete(done())
  expect(submitted).toHaveLength(0)

  agents[0] = { ...agent, status: 'completed' }
  await $.turn.start({ text: '', turnId: 't2' })
  await $.turn.complete(done())
  expect(submitted.map(s => s.text)).toEqual(['summarize'])
})

test('/later queues mid-turn, sends at once when idle, and lists/drops', async ($, on) => {
  const { submitted, clock } = world(on)
  const sent = await $.command.run(later('now please'))
  expect(sent.text).toContain('sending it now')
  await clock.advance(100)
  expect(submitted.map(s => s.text)).toEqual(['now please'])

  await $.turn.start({ text: 'now please', turnId: 't2' })
  await $.command.run(later('a'))
  await $.command.run(later('b'))
  const list = await $.command.run(later(''))
  expect(list.text).toContain('2 follow-ups queued')

  await $.command.run(later('drop 1'))
  await $.turn.complete(done())
  expect(submitted.map(s => s.text)).toEqual(['now please', 'b'])
})

const band = (isWorking: boolean) => ({
  plugin: 'followup',
  component: 'AbovePrompt' as const,
  props: {
    hasSurvey: false,
    isWorking,
    maxRows: 10,
    bodyColumns: 80,
    scroll: { offset: 0, bodyRows: 10 },
    view: {},
  },
})

test('the band lists the queue and its buttons work on every input surface', async ($, on) => {
  const { clock } = world(on)
  // The engine's own band beneath the plugin: an empty box.
  on('ui.render', ($, e) => h($.ui.resolve(e).Box, { key: 'engine' }) as RenderElement)
  for (const surface of ['terminal', 'desktop'] as const) {
    await $.turn.start({ text: 'work', turnId: `t-${surface}` })
    await $.prompt.submit(typed('write the changelog', true, `t-${surface}`))

    const ui = await $.ui.mount({ ...band(true), surface })
    expect((await ui.find({ type: 'Text', text: /1 follow-up · after this turn/ }))).toBeDefined()
    expect((await ui.find({ type: 'Text', text: /write the changelog/ }))).toBeDefined()

    await ui.press({ key: 'pause' })
    expect((await ui.find({ type: 'Text', text: /paused/ }))).toBeDefined()
    await ui.press({ key: 'clear' })
    await clock.settle()
    expect(await ui.find({ type: 'Text', text: /follow-up/ })).toBeUndefined()
    await ui.unmount()
  }
})
