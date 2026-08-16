---
owner: Main Agent
status: active
last_updated: 2026-08-16
doc_type: reference
task: CLEAN-001-POST-INDIA2
---

# Post-INDIA-2 Cleanup Authorization Proposal

## Decision

Exact candidate set `POST-INDIA2-2499DF4ADE0DF704` contains **71 branches** and **193 separately bound actions**. Its worktree actions are expected to recover approximately **7.8 GiB**. The repository owner delegated the final decision to this task; Phase A remains inspection-only, and Phase B may act only after same-session equality checks for each listed path/ref/SHA.

No worktree, local branch, remote branch, pull request, issue, stash, or retained lane was removed or altered while producing this proposal.

## Live inventory boundary

- Default anchor: `origin/main = d8202fef2566cd4955b2ba041914ff318d15d043`.
- Worktrees: 68 total now, comprising 67 pre-existing lanes plus this audit lane.
- Local branches: 71 total now, comprising 70 pre-existing refs plus this audit branch.
- GitHub branches: 86.
- Open PRs: 7, all Dependabot-managed; non-Dependabot open PRs: 0.
- Detached lanes: 5; dirty pre-existing lanes: 1 (`e54a` only). The audit lane was dirty only with the in-progress packet files at observation time.

The full union inventory, owner observations, PR/review heads, merge trees, classifier target results, surface actions, disk estimates, and recovery evidence are in [`post-india2-cleanup-disposition-evidence.json`](post-india2-cleanup-disposition-evidence.json).

## Candidate actions

| Branch | Exact head | PR / squash-tree proof | Worktree action | Local action | Remote action | Expected recovery |
|---|---|---|---|---|---|---:|
| `codex/alpha-0231-candidate-evidence` | `adb161b85489f530b42e78abd7039e59160c83d6` | #732; `4598f0a30dd9579bf5db50bd16068e8b3e85c563` = merged tree | No attached worktree | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/alpha-0231-integration` | `e3b9a6cbc35c3d4da9fbbdff975f92b88eec0c61` | #730; `19d555b6be9eb7e8639437f5dcbbb9c044e7a579` = merged tree | `/Users/pravinsurawase/.codex/worktrees/alpha0231/structural_engineering_lib` @ `e3b9a6cbc35c` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 65.2 MiB |
| `codex/alpha-0231-release-closeout` | `127afb64c52c0cac6cb3a90d0fe68fef3883b49c` | #733; `6f422cbe675f76905222af6a8ee78d06c02e44a0` = merged tree | `/Users/pravinsurawase/.codex/worktrees/alpha-candidate/structural_engineering_lib` @ `127afb64c52c` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 507.9 MiB |
| `codex/ci-fastapi-load-lane-fix` | `21b9df1fd0d655d5976f73b8672502da4a6fbc60` | #729; `f8c203becf22c78d5573d3b67cdf1ee14094a65b` = merged tree | No attached worktree | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/column-pmm-closeout` | `04f789deb672254ae421f41fb6315f304ae71af7` | #739; `91c2a6e97f640bb7dd643c4be79c9be9ef3a49bf` = merged tree | No attached worktree | `NO_ACTION_SURFACE` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/column-pmm-completion` | `a481d1ab0d49441c2914bea3201eb9eb9d9e3ce7` | #738; `a3e1fb088a11f2efc5f86c9f561cc12e0e42e00d` = merged tree | No attached worktree | `NO_ACTION_SURFACE` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/column-rectangular-e2e` | `007dfa0c012404515907779f396ed94cf7a6694d` | #725; `f32e261a930929f92300eae3858f1677c03d779b` = merged tree | No attached worktree | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/compact-orchestrator-workflow` | `0690f74504b780f7920828a7ea0cd0e0dda4149c` | #752; `8f38c8d40033010a011e9eb38c9519f3347d381c` = merged tree | `/Users/pravinsurawase/.codex/worktrees/8690/structural_engineering_lib` @ `0690f74504b7` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 65.0 MiB |
| `codex/doc-frontmatter-contract` | `b45b50cfc358e9c8f36b319d806184795a5d6171` | #802; `4de5ae83cdc115fe1984e2b97b616676e094e578` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-doc-frontmatter` @ `b45b50cfc358` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 68.0 MiB |
| `codex/git-001-phase8-reconciliation` | `392edb681cbf22758353fabfb083a1095f46cc57` | #801; `41d878c0681e5e51d159615d14290d5c3964c822` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-git-001-p8` @ `392edb681cbf` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 68.2 MiB |
| `codex/git-7b-state-kernel` | `5c22cc05f1ed42139a54ff3a4072b8dc62a1e1ae` | #744; `30036fe6df7dbc9f034220b524624b1e2dc5e6c4` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-git-7b-state-kernel` @ `5c22cc05f1ed` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 73.9 MiB |
| `codex/git-7c-ci-enforcement` | `c3edd24783df0f14efe1854f411dbc6735b44f40` | #745; `33d94f67834ea8cc669f73678022e89a927c0b02` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-git-7c-ci-enforcement` @ `c3edd24783df` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 136.3 MiB |
| `codex/git-7d1-index-routing` | `f156f9341a195a76da3f95b82b0340f7d2ff532f` | #746; `7403239db5ae397eb5d26cfdddc8ac935ef2d9e5` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-git-7c2-closeout` @ `f156f9341a19` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 135.8 MiB |
| `codex/git-7d2-disposition-classifier` | `8742061604f75ad0807cb012a1192ebf997143bf` | #747; `c6f4a6f7f65eaf3561ab226a2e9b28dfd6436eae` = merged tree | `/Users/pravinsurawase/.codex/worktrees/818e/structural_engineering_lib` @ `8742061604f7` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 136.6 MiB |
| `codex/git-7d2-session-lessons` | `cb2750b9f2c0eaf2cbecff33f3ed09db1b82585e` | #748; `2b8e3cdb32e342c43a41af98e868c717feaca646` = merged tree | `/Users/pravinsurawase/.codex/worktrees/818e-git7d2-lessons` @ `cb2750b9f2c0` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 136.6 MiB |
| `codex/git-7e-semantic-handoff` | `dd1b0ab97d6900ee97e07d3ad66d716c576a787b` | #751; `f1b38e17e932e8e84c06cca23061aec97351c699` = merged tree | `/Users/pravinsurawase/.codex/worktrees/0753/structural_engineering_lib` @ `dd1b0ab97d69` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 136.8 MiB |
| `codex/git-cleanup-reconciliation` | `d92bc347da64005aa345d79ce9ace5d41d08a111` | #749; `0833445ec0113b3731441603c92ed47edb530e3a` = merged tree | `/Users/pravinsurawase/.codex/worktrees/git-cleanup-reconciliation` @ `d92bc347da64` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 64.7 MiB |
| `codex/git-future-work-plan` | `0f324db99fb6b2fc91003a2802e04819643b2118` | #741; `c6922294843856adac84b019d7c2bea5cf325c4a` = merged tree | No attached worktree | `NO_ACTION_SURFACE` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/git-future-work-plan-closeout` | `1c70487ec298197ede4ba3f353b61ed9db75422c` | #742; `60b0e80fb8c9986e0c17e0946ddaa77009d22bbb` = merged tree | No attached worktree | `NO_ACTION_SURFACE` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/git-pmm-learning-update` | `f03c5605d40a3b7801085107a5d873979725097c` | #740; `aff9605107d9b3f4c9c3af05416e5cf7b921db38` = merged tree | No attached worktree | `NO_ACTION_SURFACE` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/git-recovery-closeout` | `234abbee43fc172d1c578d93dcb6e2754b206e9a` | #737; `facdabbbd9b0748a3f0194e63bba54e0aa737195` = merged tree | No attached worktree | `NO_ACTION_SURFACE` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/git-retirement-authorization-proposal` | `4408175e07b163af6c8ef6c223e49674ce4ba5ac` | #750; `f05c68eb3c0656d326601864a34567ef8d2b5cdf` = merged tree | `/Users/pravinsurawase/.codex/worktrees/b23a/structural_engineering_lib` @ `4408175e07b1` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 64.8 MiB |
| `codex/gpt-5-3-spark-work-program` | `6cd22dcbd073b599e4a2faef80352b294295f32e` | #734; `3cda24d03ece4075c7f76cd08a0728fbf80b869d` = merged tree | No attached worktree | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/india-0-truth-baseline` | `dd6c1f85f9a86c3c757dbfbc4e90e155630e4dab` | #753; `f02f22b7526598a21ccbf34728e92572f71442e6` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-0` @ `dd6c1f85f9a8` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 136.3 MiB |
| `codex/india-1-cumulative-gates` | `ef5443c2f0d61c6e7edbbf5724c7c416da95001e` | #758; `24dcd82563d61d743322ac7acbd8f695a79af63b` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-1-final` @ `ef5443c2f0d6` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 77.1 MiB |
| `codex/india-1a-beam-route-closure` | `5df4e9962798a6472861a944a94bb7025c1dce15` | #754; `d01342f9b302b5958bb9bc7aebbb98f9e31345e4` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-1a` @ `5df4e9962798` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 216.2 MiB |
| `codex/india-1b-column-decision-closure` | `1f10778ce4c3f0fb0d1d2b0113c638ed17b121ca` | #755; `aac24e04df5466b195f6c20d278696bef43f79e7` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-1b` @ `1f10778ce4c3` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 135.9 MiB |
| `codex/india-1c-isolated-footing-workflow` | `03a50688057c50e81975dc35df40f570dc73566d` | #756; `d797e93982bd1c5fbf12bbb8e73c329bd67b1711` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-1c` @ `03a50688057c` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 136.4 MiB |
| `codex/india-1d-slab-boundary` | `9d7fe61dc05e711c09007811b8e29e9208eb0599` | #757; `177bf403ec5c3405e617bc9786e156b406940044` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-1d` @ `9d7fe61dc05e` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 136.1 MiB |
| `codex/india-2-closeout` | `e65367210e573bc8b827529e5b8330abfbda369e` | #806; `f816500de7c8e6bfcb8b2dcb99f61bf433680c2b` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-closeout` @ `e65367210e57` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 81.3 MiB |
| `codex/india-2-deep-a` | `a916d58927846d5e6730da693c93421906dfa0f6` | #775; `c41ea26434266021885975b8f1e611baa28f210e` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-deep-a` @ `a916d5892784` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 200.0 MiB |
| `codex/india-2-deep-acceptance` | `fd3e091c36749a0085d87246393ccdd581b08082` | #779; `507d47576e8c85b6cdcaafcc31df1a7fa3a1b4a6` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-deep-acceptance` @ `fd3e091c3674` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 95.9 MiB |
| `codex/india-2-deep-b` | `d320427ffd7ad0f3a1d722a5b38319e0b143bba6` | #776; `9a90380ece7ab96a903f7bca2f95b868ffce5ddf` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-deep-b` @ `d320427ffd7a` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 165.6 MiB |
| `codex/india-2-deep-c` | `7c9aa2185c5a8da97de747633ae8a4a53ba1940c` | #777; `c1e3c17bd956d850c0c04a9e0f32816175f889ca` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-deep-c` @ `7c9aa2185c5a` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 166.6 MiB |
| `codex/india-2-deep-d` | `aa66f6a50a946d937655cb4e6aaa2785a47ab386` | #778; `966149afc07099ffd5e9256b61d58c4be1e88937` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-deep-d` @ `aa66f6a50a94` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 223.8 MiB |
| `codex/india-2-deep-g0` | `e8e6f516782c9860cc4df478a63b23e3ca720a05` | #774; `b89398c0f81b0f6e0edf31b1c85b77fcf5c98d67` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-deep-g0` @ `e8e6f516782c` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 94.2 MiB |
| `codex/india-2-detailed-plan` | `eb4dd53db63bcf5797f7f642cca16568b8a65464` | #767; `a3ecc87ca0e3ff45d54c55dc6c1a4f1a28026361` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-detailed-plan` @ `eb4dd53db63b` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 65.6 MiB |
| `codex/india-2-flat-a` | `f84d319140c0b60e9de66e1437abf4277d129212` | #781; `e3821ef47385f60d63c8ae371a7a8cdbb5b314ce` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-flat-a` @ `f84d319140c0` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 166.2 MiB |
| `codex/india-2-flat-acceptance` | `1edbb1d1af609a93aff537a8f130c75bd4a0b4e4` | #786; `81b9c61fbe94da1863571f99b72f553d77a02b62` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-flat-acceptance` @ `1edbb1d1af60` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 68.2 MiB |
| `codex/india-2-flat-b` | `95503021860957aa78920ecd782149a91c7268c7` | #782; `9579010da1a482dfe8122ac62afbf151a413157d` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-flat-b` @ `955030218609` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 166.4 MiB |
| `codex/india-2-flat-c` | `97d2413b859ccbdd92e85f6bb8b30b52bf13c541` | #783; `5e34199b7d589c8ca045a344b2e79ca42e733755` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-flat-c` @ `97d2413b859c` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 166.7 MiB |
| `codex/india-2-flat-d` | `7e3e54d50c0c31e056b637eb393a22d4ba2224c7` | #784; `98b32f40d66062948cc342800a5058de700047eb` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-flat-d` @ `7e3e54d50c0c` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 166.9 MiB |
| `codex/india-2-flat-e` | `78a0560d5847b9f10b3ac7fdd3374a50c02b52d0` | #785; `9ee6e9b2fb77087405841b07efe1b87486be05a4` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-flat-e` @ `78a0560d5847` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 236.6 MiB |
| `codex/india-2-flat-g0` | `c6daf8d4f152d483b9dc1fa1e5754655badef30b` | #780; `9ba708db80d6e3bafc64af84bcad2be6cda183f8` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-flat-g0` @ `c6daf8d4f152` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 96.8 MiB |
| `codex/india-2-foundation-combined-a` | `8adba7f69b24fcbdae7034d94a1d0f0033943e0b` | #788; `fb4483f6d5590e6c26f23388323cccdf9b2a0c68` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-combined-a` @ `8adba7f69b24` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 167.8 MiB |
| `codex/india-2-foundation-combined-acceptance` | `490b10a8e567fb6af6fa0398c90f62388da555b4` | #792; `873aea4cdca8aa9633b30a7c9b74138e5a73a6ce` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-combined-acceptance` @ `490b10a8e567` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 98.4 MiB |
| `codex/india-2-foundation-combined-b` | `948787bb56d28b8fbcca83aa94f1c68a26ec2eab` | #789; `66243e06608f9323c605f16b8ca96eaf93d04fa5` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-combined-b` @ `948787bb56d2` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 203.3 MiB |
| `codex/india-2-foundation-combined-c` | `8928309110615ca59831fc707ad627e59d78b292` | #790; `dd9ed4adf0b20de5d307689ecdf502801fad2d6e` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-combined-c` @ `892830911061` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 215.6 MiB |
| `codex/india-2-foundation-combined-d` | `7e25cfd082a2aa4f5fde857727af7c80f9bbabed` | #791; `efba5971017b03e14e3b2f30fd40750f8fc68987` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-combined-d` @ `7e25cfd082a2` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 227.7 MiB |
| `codex/india-2-foundation-combined-g0` | `f4ef757cfd41677e056d1c2881c5b3666df1efef` | #787; `697d3c13ca2be41cb5563b79197ae9856037248b` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-combined-g0` @ `f4ef757cfd41` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 67.0 MiB |
| `codex/india-2-foundation-pile-cap-g0` | `e9d6d14b7c81963aff9ed5e7fc0e092225df8429` | #804; `7da91c66143e83933a88bb9a4d5396bede89cf6d` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-pile-cap-g0` @ `e9d6d14b7c81` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 68.2 MiB |
| `codex/india-2-foundation-raft-g0` | `99215d854618fb5ad10ae37994dd86a4399f1ab6` | #805; `38958c8a484d5f63a1092b2e852af64bef7afc2a` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-raft-g0` @ `99215d854618` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 68.2 MiB |
| `codex/india-2-foundation-strap-a` | `3a4de97e5de90468fb5fa5d7a027e099a35eaf8c` | #794; `08899dbedd35e3d0b0e2c9ba2e78813d87be1f70` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-strap-a` @ `3a4de97e5de9` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 169.2 MiB |
| `codex/india-2-foundation-strap-acceptance` | `7f480cb54d898797dab3856c2cb3972ce57a110f` | #798; `28698a28d96f3e5cbad26fd6964cf835cda6e1b4` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-strap-acceptance` @ `7f480cb54d89` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 99.1 MiB |
| `codex/india-2-foundation-strap-b` | `6c721570e7d910e6b7a37c66a190b066337f7ea0` | #795; `02f3a5c0bd0de0afbda6ca3ab128b40283efde5e` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-strap-b` @ `6c721570e7d9` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 169.9 MiB |
| `codex/india-2-foundation-strap-c` | `89d3a559525524559501a206e6b0db9c2ec6d908` | #796; `40040d5433b38b6c322bb1f6a789cab1bc5e2872` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-strap-c` @ `89d3a5595255` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 171.0 MiB |
| `codex/india-2-foundation-strap-d` | `c107993b2a68cd7e92903424c89ebe3063f7f791` | #797; `af2695a815bb0a71898d58e98a70109b7dd5c2b4` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-strap-d` @ `c107993b2a68` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 246.9 MiB |
| `codex/india-2-foundation-strap-g0` | `ceb09acc3dec39a34865dea41ad426b89420ebc4` | #793; `60d5636265e157e723236909b1de7f582791b297` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-foundation-strap-g0` @ `ceb09acc3dec` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 67.5 MiB |
| `codex/india-2-next-agent-plan-refresh` | `57c58b7173d7fb69452e46237d5502eec52dbddd` | #800; `1bb7e448fd26208ba2227b1d9e2f3f0f976ed46e` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-next-agent-plan` @ `57c58b7173d7` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 68.2 MiB |
| `codex/india-2-next-session-git-issues-plan` | `81368eaeed3540ad8c2d356e89e5eef8bb4efbff` | #799; `ecd7fe389409e4077afb37f17aee20fe5734cf0e` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-next-session-plan` @ `81368eaeed35` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 68.0 MiB |
| `codex/india-2-truth-hygiene-38-2` | `eb33120d0e20d828ff2dea0d11a1e2fb99a0ffb5` | #803; `0abefcd0255157bd1444549f2066eb937f45e5a0` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-38-2` @ `eb33120d0e20` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 143.7 MiB |
| `codex/india-2-wall-a` | `a0791756d5ab3592fab37fb5361382f02239b394` | #769; `62ea7b808c18af73d9e56e35ac51dd3e9c0ded70` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-wall-a` @ `a0791756d5ab` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 164.5 MiB |
| `codex/india-2-wall-acceptance` | `34efa769ab7122ca2a9bd3f8197b7a2cc5aaa1d9` | #773; `1512923877c29d1bb0da6ffe849a9bfd28f890bd` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-wall-acceptance` @ `34efa769ab71` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 172.8 MiB |
| `codex/india-2-wall-b` | `fc53873a8e227e4764d178586f919b77aca89e3a` | #770; `db1fdfb97fa12867826fa55c05f7bacc4a3b3e59` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-wall-b` @ `fc53873a8e22` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 164.7 MiB |
| `codex/india-2-wall-c` | `38276066fb42306977d76c560bcd585bfc79a8ce` | #771; `e065dbdb3636fcebfe1fda444f99cd461e26beb5` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-wall-c` @ `38276066fb42` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 165.7 MiB |
| `codex/india-2-wall-d` | `9a24c601a493a56549c1f4aed1293dd79af4c6ec` | #772; `8a5a5e0e310d2b72e3081da14cfdd5b557ddcdf7` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-wall-d` @ `9a24c601a493` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 222.6 MiB |
| `codex/india-2-wall-g0` | `5bec2e5bc25d910ea5c3701301a58cc3cf75f1fa` | #768; `4766ea1dd086f7766293b87506f55e6fe071bc64` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-2-wall-g0` @ `5bec2e5bc25d` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 66.1 MiB |
| `codex/india-finish-plan-reconcile` | `24a08a868f1ae1aaffacf840a45d40f2f2183922` | #766; `21ad46ae0312f5f47cbee47eaf186e08df9bb1a1` = merged tree | `/Users/pravinsurawase/VS_code_project/structural_engineering_lib-india-finish-plan` @ `24a08a868f1a` | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 65.6 MiB |
| `codex/is456-beam-primary-route` | `aa4fe606ee685240648c88db75e0d1052350fcb4` | #726; `ee8c6f486236773b24188c30747ac9d340c445ca` = merged tree | No attached worktree | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/is456-slabs-closeout` | `d79a1558a0cfa5078f6ddea91c4166100bdc4d04` | #724; `8fffc7dc2160a35a5deab81d7cf9dbb529783d3c` = merged tree | No attached worktree | `DELETE_WITH_GIT_BRANCH_D` | `DELETE_EXACT_REMOTE_REF` | 0 B |
| `codex/workflow-intake-recovery` | `aec9fbb2371dc63b2c3b33b465fc85eab18558f4` | #736; `7b70c5f2a997db5537715a631007c164d1bc39da` = merged tree | No attached worktree | `NO_ACTION_SURFACE` | `DELETE_EXACT_REMOTE_REF` | 0 B |

Every candidate retains recovery evidence in the JSON packet: exact branch head/tree, merged PR URL, merge commit/tree, and the proof that the merged commit is reachable from current `origin/main`. Deleting refs does not immediately reclaim Git object storage; only worktree directories contribute to the stated disk estimate.

## Classifier boundary

The integrated classifier was run over every pre-existing non-main local branch with fresh caller-supplied remote, PR, owner, and retention evidence. The JSON packet retains each target's exact disposition, reasons, identities, graph/tree facts, query failures, and next action; duplicate input structures are represented once in the union rows. Clean attached worktrees correctly remain `HOLD_ATTACHED_OR_DIRTY` until their separately authorized worktree removal; squash-equivalent branches remain `PATCH_EQUIVALENT_REVIEW_REQUIRED` until the exact PR-head/merge-tree comparison recorded here is accepted. These are stage-order holds, not deletion shortcuts.

Phase B must first re-check every worktree path/HEAD/clean/lock/operation fact, remove an approved clean worktree without force, rerun the classifier after detachment, and require the exact local/remote SHA before normal `git branch -d` or exact remote-ref deletion. Any mismatch converts that target to HOLD.

## Frozen holds and exclusions

| Branch / surface | Decision | Reason |
|---|---|---|
| `codex/column-pmm-experimental` | `HOLD` | OWNER_UNKNOWN_NO_ASSOCIATED_PR_AUTHOR, NO_EXACT_MERGED_PR_HEAD |
| `codex/excel-product-planning` | `HOLD` | EXCEL_PLANNING_LANE, OWNER_RETENTION_UNRESOLVED |
| `codex/footing-isolated-v1` | `HOLD` | SQUASH_MERGE_TREE_MISMATCH_OR_UNAVAILABLE |
| `codex/git-governance-research` | `HOLD` | LOCAL_REMOTE_HEAD_MISMATCH, NO_EXACT_MERGED_PR_HEAD |
| `codex/is456-slabs-plan` | `HOLD` | SQUASH_MERGE_TREE_MISMATCH_OR_UNAVAILABLE |
| `codex/parallel-task-policy` | `HOLD` | NO_EXACT_MERGED_PR_HEAD |
| `codex/post-india2-cleanup-audit` | `RETAIN` | CURRENT_AUDIT_PACKET_LANE |
| `codex/release-preflight-alpha-policy` | `HOLD` | LOCAL_REMOTE_HEAD_MISMATCH, NO_EXACT_MERGED_PR_HEAD |
| `dependabot/npm_and_yarn/react_app/eslint-10.8.0` | `EXCLUDED_SYSTEM_MANAGED` | DEPENDABOT_MANAGED_BRANCH |
| `dependabot/npm_and_yarn/react_app/eslint/js-10.0.1` | `EXCLUDED_SYSTEM_MANAGED` | DEPENDABOT_MANAGED_BRANCH |
| `dependabot/npm_and_yarn/react_app/framer-motion-13.0.0` | `EXCLUDED_SYSTEM_MANAGED` | DEPENDABOT_MANAGED_BRANCH |
| `dependabot/npm_and_yarn/react_app/types/node-26.1.2` | `EXCLUDED_SYSTEM_MANAGED` | DEPENDABOT_MANAGED_BRANCH |
| `dependabot/npm_and_yarn/react_app/vitejs/plugin-react-6.0.5` | `EXCLUDED_SYSTEM_MANAGED` | DEPENDABOT_MANAGED_BRANCH |
| `dependabot/pip/Python/mypy-gte-1.19-and-lt-3` | `EXCLUDED_SYSTEM_MANAGED` | DEPENDABOT_MANAGED_BRANCH |
| `dependabot/pip/mypy-2.3.0` | `EXCLUDED_SYSTEM_MANAGED` | DEPENDABOT_MANAGED_BRANCH |
| `gh-pages` | `RETAIN` | PUBLISHED_DOCUMENTATION_BRANCH |
| `main` | `RETAIN` | DEFAULT_BRANCH_INTEGRATION_ANCHOR |
| `/Users/pravinsurawase/.codex/worktrees/5986/structural_engineering_lib` @ `b91838f594a04aff1d21c43bf6f87a64710b0748` | `HOLD` | DETACHED_LANE |
| `/Users/pravinsurawase/.codex/worktrees/b026/structural_engineering_lib` @ `670ea4beeb2a8765fff59e05bb130ff54752369e` | `HOLD` | DETACHED_LANE |
| `/Users/pravinsurawase/.codex/worktrees/b94c/structural_engineering_lib` @ `bf4065f071f1245461df6d3c42f1cc070efbae70` | `HOLD` | DETACHED_LANE |
| `/Users/pravinsurawase/.codex/worktrees/e54a/structural_engineering_lib` @ `0fdb48edbb73114288feb8a246d6f30b80ac4d95` | `RETAIN` | EXPLICIT_E54A_EXCLUSION, DIRTY_DETACHED_LANE |
| `/Users/pravinsurawase/.codex/worktrees/fa98/structural_engineering_lib` @ `b91838f594a04aff1d21c43bf6f87a64710b0748` | `HOLD` | DETACHED_LANE |

## Phase B authorization and stop rules

The owner's active-task delegation authorizes this task to decide and execute candidate set `POST-INDIA2-2499DF4ADE0DF704` without another approval round. That authority is exact-target and fail-closed; it does not extend to any held or excluded surface, release, issue/PR closure, force operation, broad prune, or history rewrite.

Stop a target immediately if its path/ref/SHA changed, became dirty, locked, detached, operation-bearing, open-PR-dependent, or otherwise inconsistent with this packet. Record removed, retained, held, failed, and recovered totals in the execution receipt.

## Issues encountered

- The inherited baseline said no PRs were open; the live query found seven Dependabot PRs. Their system-managed   branches were already excluded, so the candidate outcome did not change.
- The first linked-worktree diagnosis was accidentally invoked from the primary checkout immediately after   `git worktree add`; no write occurred there, and all evidence commands were rerun with the audit worktree   supplied as the explicit working directory.
- The first complete generator pass failed while reading `mergeCommit.oid` from an open PR, where GitHub   correctly returns a null merge object. No partial evidence file was produced.
- The first strict metadata check rejected `doc_type: verification`, which is not one of the repository's   canonical metadata values.
- The first commit attempt was blocked because the indented JSON repeated classifier input and output and   exceeded the repository's 500 KB evidence-file limit; no commit was created.
- The first full repository gate passed 29/30 and failed only the 400-document hard limit after the required   new Markdown proposal raised the non-archived count to 401.

## Root causes and resolutions

- GitHub state changed after the planning snapshot. Resolution: live `gh pr list --state all` and branch API   observations are stored in the packet; all open Dependabot heads remain excluded.
- `git worktree add` creates the lane but does not change the caller's process working directory. Resolution:   every subsequent command uses the linked worktree as its explicit working directory, and source binding was   re-proved before evidence collection.
- The generator assumed every PR had a merge object. Resolution: normalize nullable `mergeCommit` values   before accessing the OID; the full 86-remote-branch evidence build then completed and JSON parsing passed.
- The evidence category had been used as a metadata type. Resolution: retain the file under   `docs/verification/` but use canonical `doc_type: reference`; the repeated strict frontmatter check passes.
- The union rows, classifier input, and classifier output serialized the same PR/worktree facts multiple times.   Resolution: remove duplicate projections, retain every decision-bearing field, and use compact JSON; the file   is 329,393 bytes, its candidate-set hash is unchanged, and all invariants pass.
- The repository was already at its 400-document ceiling. Resolution: use the required safe-file mover, with a   dry-run first, to archive the explicitly superseded Git-workflow hardening plan and update its two maintained   links; `_active/README.md` now truthfully reports two remaining plans. The corrective full gate must pass.
