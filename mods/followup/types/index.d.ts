export type FollowupQueue = string[]

declare module 'claude-code' {
  interface PluginState {
    followup: { queue: FollowupQueue; isPaused: boolean; isBusy: boolean }
  }
}
