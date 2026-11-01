import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, realpathSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const root = realpathSync(mkdtempSync(join(tmpdir(), 'terminal-toolkit-')));
const project = join(root, 'project with spaces');
const cleanDirenv = Object.fromEntries(
  Object.entries(process.env).filter(([key]) => !key.startsWith('DIRENV_')),
);
const direnvEnv = {
  ...cleanDirenv,
  DIRENV_CONFIG: join(root, 'direnv-config'),
  XDG_DATA_HOME: join(root, 'direnv-data'),
};

function run(command, args, options = {}) {
  const { status = 0, ...rest } = options;
  const result = spawnSync(command, args, {
    cwd: project, encoding: 'utf8', timeout: 15000, ...rest,
  });
  assert.ifError(result.error);
  assert.equal(result.status, status, `${command}: ${result.stderr}`);
  return result.stdout;
}

try {
  for (const dir of [project, join(project, 'src'), join(project, 'docs'),
    join(project, 'node_modules'), direnvEnv.DIRENV_CONFIG, direnvEnv.XDG_DATA_HOME]) {
    mkdirSync(dir, { recursive: true });
  }
  run('git', ['init', '--quiet']);
  writeFileSync(join(project, '.gitignore'), 'node_modules/\n');
  writeFileSync(join(project, 'src/input file.ts'), 'export const toolkitFixture = 7;\n');
  writeFileSync(join(project, 'node_modules/ignored.ts'), 'toolkitFixture should be ignored\n');
  writeFileSync(join(project, 'docs/-draft.md'), '# Path safety fixture\n');

  const matches = run('rg', ['-n', '--', 'toolkitFixture', '.']);
  assert.match(matches, /input file\.ts/);
  assert.ok(!matches.includes('node_modules'));
  const filenames = run('fd', ['--fixed-strings', 'input file.ts', '.']);
  assert.match(filenames, /src\/input file\.ts/);
  assert.match(run('bat', ['--paging=never', '--color=never', '--line-range', '1:1',
    '--', 'src/input file.ts']), /toolkitFixture = 7/);
  assert.match(run('fzf', ['--filter=input'], { input: filenames }), /input file\.ts/);
  run('fzf', ['--filter=no-such-candidate'], { input: filenames, status: 1 });
  assert.match(run('bash', ['-o', 'pipefail', '-c',
    'fd --type f -e md -0 . docs | xargs -0 bat --paging=never --color=never --']),
  /Path safety fixture/);

  const zoxideEnv = { ...process.env, _ZO_DATA_DIR: join(root, 'zoxide-data') };
  mkdirSync(zoxideEnv._ZO_DATA_DIR);
  run('zoxide', ['add', '--', project], { env: zoxideEnv });
  assert.equal(run('zoxide', ['query', '--', 'project with spaces'],
    { env: zoxideEnv }).trim(), project);

  // Verify direnv supplies environment variables without changing the caller's cwd.
  assert.equal(run('direnv', ['exec', project, 'pwd'],
    { cwd: root, env: direnvEnv }).trim(), root);
  writeFileSync(join(project, '.envrc'), 'export TOOLKIT_SMOKE_VALUE=toolkit-ok\n');
  assert.equal(run('direnv', ['exec', project, 'sh', '-c',
    'printf %s "$TOOLKIT_SMOKE_VALUE"'], { env: direnvEnv, status: 1 }), '');
  run('direnv', ['allow', project], { env: direnvEnv });
  assert.equal(run('direnv', ['exec', project, 'sh', '-c',
    'printf %s "$TOOLKIT_SMOKE_VALUE"'], { env: direnvEnv }), 'toolkit-ok');
  console.log('Toolkit smoke checks passed: file selection, ignore rules, path safety, project lookup, and isolated environment trust.');
} finally {
  rmSync(root, { recursive: true, force: true });
}
