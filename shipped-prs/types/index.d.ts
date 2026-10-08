export type PrState = 'open' | 'draft' | 'merged' | 'closed'

export type Pr = {
  number: number
  repo: string
  url: string
  title: string
  state: PrState
}

declare module 'claude-code' {
  interface PluginState {
    'shipped-prs': { prs: Pr[]; isHidden: boolean }
  }
}
