# Portfolio release walkthrough

This checklist creates the demo content manually. Do not add real credentials
to the fixture or commit generated screenshots containing secrets.

1. Create the branch locally:

   ```bash
   git switch main
   git pull
   git switch -c demo/seeded-bugs
   ```

2. Copy the snippets from `docs/demo_seeded_bugs.py` into a small source file
   in that branch. Keep the fixture non-executable and make a commit.
3. Push the branch and open a pull request against `main` in GitHub. Confirm
   that the live review workflow is enabled and let it run to completion.
4. Capture the actual summary issue comment and inline review comments. Verify
   that locations and suggestions correspond to the changed lines.
5. Save a redacted screenshot of the real review as `docs/demo-review.png`.
6. Update the README Example or Demo preparation section to link the real PR
   and embed it with `![Demo review](docs/demo-review.png)`, then commit that
   documentation update if desired.
7. Keep the demo pull request available so portfolio viewers can inspect the
   actual review and workflow run.

The repository intentionally does not create the branch, pull request,
screenshot, or GitHub content for you.
