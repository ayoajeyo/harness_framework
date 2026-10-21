# 외부 자료 출처 (Third-party notices)

## mattpocock/skills — MIT License
아래 파일은 https://github.com/mattpocock/skills (커밋 49dd158, 2026-10-09) 의 스킬을 이 하네스에 맞게 **한국어로 옮기고 고친 것**이다.
경로·문서 구조(docs/GLOSSARY.md, docs/ADR.md, docs/PLANS, BACKLOG)와 초보자용 설명은 이 하네스에 맞게 바꿨다.

| 이 저장소 | 원본 |
|-----------|------|
| `.claude/commands/wait-what.md` | `skills/productivity/wait-what` |
| `.claude/commands/retro.md` | `skills/engineering/retro` |
| `.claude/commands/grill-with-docs.md`, `.claude/skills/doc-grilling/` | `skills/engineering/grill-with-docs`, `skills/productivity/grilling`, `skills/engineering/domain-modeling` |
| `.claude/commands/improve-codebase-architecture.md`, `.claude/skills/codebase-design/` | `skills/engineering/improve-codebase-architecture`, `skills/engineering/codebase-design` |

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## obra/superpowers — MIT License (© 2025 Jesse Vincent)
https://github.com/obra/superpowers 의 스킬 13개를 넣었다. 시작 훅(SessionStart)·`using-superpowers`·`diagnosing-superpowers` 는 모든 대화에서 스킬을 강제해 `/feature`·`/fix`·`/ship` 하네스와 부딪혀 **뺐다**. `brainstorming` 은 큰 기능일 때만 자동으로 쓰게 설명·저장 위치(`docs/PLANS/`)·다음 단계(`/feature`)를 하네스에 맞춰 고쳤다. 하네스와 겹치는 writing-plans·executing-plans·subagent-driven-development·using-git-worktrees·finishing-a-development-branch·requesting-code-review 는 `disable-model-invocation: true`(사용자가 부를 때만).

| 이 저장소 파일 | 원본 |
|---|---|
| `.claude/skills/{brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, verification-before-completion, writing-plans, writing-skills}/` | `skills/` 같은 이름 |

전문은 각 폴더의 `LICENSE`.

## nextlevelbuilder/ui-ux-pro-max — MIT License (© 2024 Next Level Builder)
`.claude/skills/ui-ux-pro-max/` 하나만(테스트 폴더 제외). 사용자가 `/ui-ux-pro-max` 로 부를 때만 쓴다. 전문은 폴더의 `LICENSE`.

## JuliusBrussee/caveman — Apache License 2.0
`.claude/skills/{caveman, ultracave, megacave, caveman-help}/` 4개(짧은 말투). 부를 때만. 전문은 각 폴더의 `LICENSE`.

## davila7/claude-code-templates — MIT License (© 2025 Daniel Ávila)
에이전트 3개를 한국어·읽기 전용·자동 실행 없음으로 옮기고 고쳤다. 통째 설치(`npx claude-code-templates@latest`)는 외부 최신 코드를 바로 실행하고 하네스와 겹쳐 하지 않았다.

| 이 저장소 파일 | 원본 |
|---|---|
| `.claude/agents/a11y-checker.md` | `agents/web-tools/web-accessibility-checker.md` |
| `.claude/agents/speed-checker.md` | `agents/performance-testing/web-vitals-optimizer.md` |
| `.claude/agents/supabase-checker.md` | `agents/database/supabase-schema-architect.md` |
