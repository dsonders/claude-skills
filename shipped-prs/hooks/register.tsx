import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Pr, PrState } from '../types'

const prs = atom({ plugin: 'shipped-prs', key: 'prs' } as const, [])
const isHidden = atom({ plugin: 'shipped-prs', key: 'isHidden' } as const, false)

const PR_URL = /https:\/\/github\.com\/([\w.-]+\/[\w.-]+)\/pull\/(\d+)/g
const REFRESH_MS = 60_000
/** Below this many body columns the band shows numbers only. */
const NARROW = 90

const MARK: Record<PrState, string> = { open: '○', draft: '◌', merged: '✓', closed: '✗' }
const COLOR: Record<PrState, 'subtle' | 'warning' | 'success' | 'error'> = {
  open: 'warning',
  draft: 'subtle',
  merged: 'success',
  closed: 'error',
}

function titleFromCommand(command: string): string {
  const m =
    command.match(/(?:--title|-t)\s+"((?:[^"\\]|\\.)*)"/) ??
    command.match(/(?:--title|-t)\s+'([^']*)'/) ??
    command.match(/(?:--title|-t)\s+([^\s]+)/)
  return (m?.[1] ?? '').replace(/\\"/g, '"')
}

function stateFromGh(gh: { state?: string; isDraft?: boolean }): PrState {
  if (gh.state === 'MERGED') return 'merged'
  if (gh.state === 'CLOSED') return 'closed'
  return gh.isDraft ? 'draft' : 'open'
}

async function addPr($: EngineInterface, pr: Pr) {
  await update($, prs, list => {
    const i = list.findIndex(one => one.repo === pr.repo && one.number === pr.number)
    if (i === -1) return [...list, pr]
    const old = list[i]!
    return list.map((one, j) => (j === i ? { ...old, ...pr, title: pr.title || old.title } : one))
  })
}

/** Asks gh for one PR: by repo+number, or by number alone in the session's repo. */
async function lookup($: EngineInterface, ref: string, repo?: string): Promise<Pr | undefined> {
  const argv = ['gh', 'pr', 'view', ref, '--json', 'number,title,state,isDraft,url']
  if (repo) argv.push('--repo', repo)
  try {
    const ran = await $.process.run(argv, { timeoutMs: 15_000 })
    if (ran.exitCode !== 0) return undefined
    const gh = JSON.parse(ran.stdout) as {
      number: number
      title: string
      state: string
      isDraft: boolean
      url: string
    }
    const m = /github\.com\/([\w.-]+\/[\w.-]+)\/pull\//.exec(gh.url)
    return {
      number: gh.number,
      repo: m?.[1] ?? repo ?? '',
      url: gh.url,
      title: gh.title,
      state: stateFromGh(gh),
    }
  } catch {
    return undefined
  }
}

/** Re-reads every PR that can still change, plus any missing a title. */
async function refreshAll($: EngineInterface) {
  const list = await read($, prs)
  const stale = list.filter(pr => pr.state === 'open' || pr.state === 'draft' || pr.title === '')
  for (const pr of stale) {
    const fresh = await lookup($, String(pr.number), pr.repo)
    if (fresh) await addPr($, fresh)
  }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'prs',
      description: 'Shipped PRs band: /prs toggles it; /prs add <n|url>, /prs refresh, /prs clear',
    })
    $.clock.every(REFRESH_MS, () => void refreshAll($))

    return next(e)
  })

  on('command.run', { command: 'prs' }, async ($, e) => {
    const [verb, ...rest] = e.args.trim().split(/\s+/)
    const arg = rest.join(' ')
    if (verb === 'add' && arg) {
      const m = /github\.com\/([\w.-]+\/[\w.-]+)\/pull\/(\d+)/.exec(arg)
      const found = m ? await lookup($, m[2]!, m[1]!) : await lookup($, arg.replace(/^#/, ''))
      if (!found) return { text: `Could not read PR ${arg} with gh.` }
      await addPr($, found)
      await update($, isHidden, () => false)
      return { text: `Added #${found.number} ${found.title}` }
    }
    if (verb === 'refresh') {
      await refreshAll($)
      const n = (await read($, prs)).length
      return { text: `Refreshed ${n} PR${n === 1 ? '' : 's'}.` }
    }
    if (verb === 'clear') {
      await update($, prs, () => [])
      return { text: 'Cleared the shipped PRs list.' }
    }
    const hidden = !(await read($, isHidden))
    await update($, isHidden, () => hidden)
    return { text: hidden ? 'Shipped PRs band hidden. /prs shows it again.' : 'Shipped PRs band shown.' }
  })

  on('tool.call', { tool: 'Bash' }, async ($, e, next) => {
    const ran = await next(e)
    if (ran.deny !== undefined || !/\bgh\s+pr\s+(create|merge)\b/.test(e.command)) return ran

    if (/\bgh\s+pr\s+create\b/.test(e.command) && ran.isError !== true) {
      const out = `${ran.result.stdout}\n${ran.result.stderr}`
      for (const m of out.matchAll(PR_URL)) {
        await addPr($, {
          number: Number(m[2]),
          repo: m[1]!,
          url: m[0],
          title: titleFromCommand(e.command),
          state: /\s--draft\b/.test(e.command) ? 'draft' : 'open',
        })
      }
    } else {
      // gh pr merge: the state may have moved; re-read in the background.
      void refreshAll($)
    }

    return ran
  }).catch(($, e, next) => next(e))

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const list = await read($, prs)
    if (e.props.hasSurvey || (await read($, isHidden))) return next(e)

    const { Box, Text } = $.ui.resolve(e)
    if (list.length === 0) {
      return (
        <Box>
          <Text dimColor>PRs: none shipped yet</Text>
        </Box>
      )
    }
    const width = e.props.bodyColumns
    const merged = list.filter(pr => pr.state === 'merged').length
    const label = `PRs ${merged}/${list.length} merged`

    if (width < NARROW) {
      return (
        <Box>
          <Text dimColor>{label} </Text>
          {list.map(pr => (
            <Text key={`pr-${pr.number}`} color={COLOR[pr.state]}>
              {' '}#{pr.number}{MARK[pr.state]}
            </Text>
          ))}
        </Box>
      )
    }

    const room = Math.max(1, e.props.maxRows - 1)
    const shown = list.slice(-room)
    const numberWidth = Math.max(...shown.map(pr => String(pr.number).length)) + 1
    return (
      <Box flexDirection="column">
        <Text dimColor>
          {label}
          {shown.length < list.length ? ` (last ${shown.length})` : ''}
        </Text>
        {shown.map(pr => (
          <Box key={`pr-${pr.number}`}>
            <Text color={COLOR[pr.state]}>
              {MARK[pr.state]} {`#${pr.number}`.padEnd(numberWidth)} {pr.state.padEnd(6)}
            </Text>
            <Text wrap="truncate-end"> {pr.title || pr.url}</Text>
          </Box>
        ))}
      </Box>
    )
  })
}
