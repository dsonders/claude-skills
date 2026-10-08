import { test, expect } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'

/** Runs /prs <args> as the person would type it (the engine stamps the rest). */
const prs = ($: Engine, args: string) =>
  $.command.run({ command: 'prs', args } as Parameters<Engine['command']['run']>[0])

const CREATE =
  'gh pr create --title "DealerBuilt picker: imported RO stays listed" --body "x"'
const URL = 'https://github.com/dsonders/ro-bot/pull/2318'

const BAND = {
  plugin: 'shipped-prs',
  component: 'AbovePrompt',
} as const

const props = (bodyColumns: number) => ({
  hasSurvey: false,
  isWorking: false,
  maxRows: 10,
  bodyColumns,
  scroll: { offset: 0, bodyRows: 9 },
  view: {},
})

test('the band is on from the start, with an empty state', async $ => {
  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...BAND, surface, props: props(100) })
    expect(await ui.find({ type: 'Text', text: /none shipped yet/ })).toBeDefined()
    await ui.unmount()
  }
})

test('a gh pr create lands in the band: numbers narrow, titles wide', async ($, on) => {
  on('tool.call', { tool: 'Bash' }, () => ({
    result: { stdout: `${URL}\n`, stderr: '', interrupted: false },
  }))

  await $.tool.call({ tool: 'Bash', command: CREATE })

  for (const surface of ['terminal', 'desktop'] as const) {
    const narrow = await $.ui.mount({ ...BAND, surface, props: props(70) })
    expect(await narrow.find({ type: 'Text', text: /#2318○/ })).toBeDefined()
    expect(await narrow.find({ type: 'Text', text: /DealerBuilt/ })).toBeUndefined()
    await narrow.unmount()

    const wide = await $.ui.mount({ ...BAND, surface, props: props(140) })
    expect(await wide.find({ type: 'Text', text: /#2318/ })).toBeDefined()
    expect(await wide.find({ type: 'Text', text: /DealerBuilt picker/ })).toBeDefined()
    await wide.unmount()
  }
})

test('/prs refresh re-reads an open PR through gh and shows it merged', async ($, on) => {
  on('tool.call', { tool: 'Bash' }, () => ({
    result: { stdout: `${URL}\n`, stderr: '', interrupted: false },
  }))
  on('process.run', () => ({
    value: {
    exitCode: 0,
    stdout: JSON.stringify({
      number: 2318,
      title: 'DealerBuilt picker: imported RO stays listed',
      state: 'MERGED',
      isDraft: false,
      url: URL,
    }),
    stderr: '',
    isStdoutTruncated: false,
    isStderrTruncated: false,
    },
  }))

  await $.tool.call({ tool: 'Bash', command: CREATE })
  const ran = await prs($, 'refresh')
  expect(ran.text).toMatch(/Refreshed 1 PR/)

  const wide = await $.ui.mount({ ...BAND, surface: 'terminal', props: props(140) })
  expect(await wide.find({ type: 'Text', text: /✓ #2318/ })).toBeDefined()
  await wide.unmount()
})

test('/prs hides the band and shows it again', async ($, on) => {
  on('ui.render', { component: 'AbovePrompt' }, ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text key="bottom">bottom</Text>
  })
  on('tool.call', { tool: 'Bash' }, () => ({
    result: { stdout: `${URL}\n`, stderr: '', interrupted: false },
  }))
  await $.tool.call({ tool: 'Bash', command: CREATE })

  await prs($, '')
  const hidden = await $.ui.mount({ ...BAND, surface: 'terminal', props: props(140) })
  expect(await hidden.find({ type: 'Text', text: /#2318/ })).toBeUndefined()
  await hidden.unmount()

  await prs($, '')
  const shown = await $.ui.mount({ ...BAND, surface: 'terminal', props: props(140) })
  expect(await shown.find({ type: 'Text', text: /#2318/ })).toBeDefined()
  await shown.unmount()
})
