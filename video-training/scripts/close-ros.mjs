// Close the throwaway repair orders a recording made, as the user who made them.
//
//   node close-ros.mjs <project-dir> <email> <org-id> [ro-id ...]
//
// With no ids it closes every id listed in <project-dir>/created-ros.txt.
// Closing is the cleanup: deleting is a bulk data operation and is Dave's call.
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { APP, BASE, password } from './lib.mjs';

const [dir, email, org, ...ids] = process.argv.slice(2);
if (!dir || !email || !org) throw new Error('usage: close-ros.mjs <project-dir> <email> <org-id> [ro-id ...]');
const file = `${resolve(dir)}/created-ros.txt`;
const list = ids.length ? ids : existsSync(file) ? readFileSync(file, 'utf8').split('\n').filter(Boolean) : [];
const { env } = await import(`${APP}/__tests__/workflow/live-pass/lib.mjs`);
const r = await fetch(`https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${env().VITE_FIREBASE_API_KEY}`, {
  method: 'POST', headers: { 'content-type': 'application/json' },
  body: JSON.stringify({ email, password: password(), returnSecureToken: true }),
});
const token = (await r.json()).idToken;
if (!token) throw new Error('login failed');
for (const id of list) {
  const c = await fetch(`${BASE}/api/repair-orders/${id}`, {
    method: 'PATCH',
    headers: { authorization: `Bearer ${token}`, 'X-Org-Id': org, 'content-type': 'application/json' },
    body: JSON.stringify({ workflowStatus: 'closed' }),
  });
  console.log(id, c.status === 200 ? 'closed' : `not closed (${c.status})`);
}
