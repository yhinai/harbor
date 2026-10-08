# Development-panel trajectory evidence

**Verified — review scope.** One assistant reviewed bounded command/result windows for every completed attempt and selected explanatory assistant windows, with expanded inspection of some candidate repairs. Not every reasoning token, entire generated source file or auxiliary test was read. Raw JSONL step indices include streamed chunks, so they are not action counts. Some windows were truncated; notes use only visible events and leave unresolved causes unknown. Automated extraction is descriptive; causal judgments are inferred.

**Verified — exclusions.** Smokes are excluded. Output, transport, protocol, turn and budget limits are reported as censored observations, even when an unfinished program appears promising. A timeout returned as a tool result is recoverable and is not by itself a censored trial. The final Harbor result determines the observed reward.

**Inferred — causal limits.** A successful final artifact establishes that this attempt solved the behavior checked by the grader. A failed artifact alone does not identify the first wrong commitment; a mechanism diagnosis below cites the concrete commands/results that support it. No target trajectory exists.

## typecheck-soundness-witness

**Verified:** Completed successful attempts from all three families construct accepted programs with concrete type errors. DeepSeek replicate 2 first tries random generation without success, then builds a structured closure/loop example (48822–49094). Kimi replicate 3 explicitly explains the missing nested-write signature (17271). **Inferred:** Direct semantic successes refute a strong claim that this flaw is beyond these proxies. The negative 15-minute baseline establishes only resistance to that generator, not model difficulty. Transport, output and budget censors supply no pass-rate failures.

### deepseek-v4p1-flash · replicate 1 · excluded: output_limit

Raw trial: `typecheck-soundness-witness__uUNFYPp`. Trajectory SHA-256: `5170e499eff799d034515348933272b01795f57f80205fc2e07817c1c4871c36`.

**Verified — events.** 45–46 reads language; 136–137 reads implementation; response 65648 has finish_reason=length and 65,536 completion tokens; 65649 raises an empty-response protocol exception. The reasoning tail has reached the nested-write signature issue but no candidate is submitted.

**Inferred — crux.** partially: the final reasoning window discusses nested effects omitted from the signature

**Inferred — commitment.** No submitted wrong program is observed.

**Inferred — recovery.** Unknown: output truncation prevents observing a completed construction.

**Mechanism judgment.** Inferred: informative output censoring, not a semantic failure or evidence of frontier hardness. Do not code as 0/1.

### deepseek-v4p1-flash · replicate 2 · reward 1.0

Raw trial: `typecheck-soundness-witness__mFtV8NS`. Trajectory SHA-256: `5a7ab5b1ff5056bbf2cd46bd2833e5b5ee3da6a5519e03d4d539405f7242cd9a`.

**Verified — events.** 17703–17912 repairs malformed block nesting, then observes static rejection; 28600–28809 random search finds no qualifying program; 48822–48823 constructs a witness; 49093–49094 confirms acceptance and type error at step 34; 49597 finishes.

**Inferred — crux.** Yes: stale nested effects.

**Inferred — commitment.** An early experiment had invalid block nesting and a later one was statically rejected.

**Inferred — recovery.** Verified: a different construction produces the qualifying type error.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### deepseek-v4p1-flash · replicate 3 · reward 1.0

Raw trial: `typecheck-soundness-witness__SEZeoVd`. Trajectory SHA-256: `8a35a75760ae0e15fdfcfa264d3ddee0cb0f8c7804daee273d043155d4872bdd`.

**Verified — events.** 25950–25951 writes an accepted program with a type error at step 40; 26104–26105 confirms exit 0 and 553-byte JSON; 26582 explains cached nested-write omission; 26583 finishes.

**Inferred — crux.** Yes: nested returned-function effects across the loop.

**Inferred — commitment.** No failed candidate observed.

**Inferred — recovery.** No recovery needed.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### glm-5p3 · replicate 1 · reward 1.0

Raw trial: `typecheck-soundness-witness__E8rhuND`. Trajectory SHA-256: `1377b287c2ff9223593b1119fc700c00544ad16d3502ffdbe99994dae36735ed`.

**Verified — events.** 43–100 reads language, checker and interpreter; 1638–1639 reads structural validation; 34842–34843 constructs loop-carried h/g/f functions and observes an accepted type error; 34985–34986 confirms 524 bytes and 31 nodes; 35396 explains the stale nested effect; the interpreter reports type_error at step 32.

**Inferred — crux.** yes

**Inferred — commitment.** No failed candidate is observed; the construction explicitly propagates a cell-writing closure through a loop-carried factory.

**Inferred — recovery.** No concrete failed-candidate recovery was required.

**Mechanism judgment.** Inferred: a second family directly solves the proposed crux, weakening transfer of the negative random baseline into a frontier-hardness forecast.

### glm-5p3 · replicate 2 · excluded: budget_limit

Raw trial: `typecheck-soundness-witness__vgiSmkc`. Trajectory SHA-256: `c6afdffa854faac5ec2f310e9209aeb021347d29c4dcf778bf8e86f237bef3c7`.

**Verified — events.** 51–102 reads implementations; 33610–33611 cannot create /work; 35691–35692 runs random programs in /tmp, 2640 accepted and normal; 66092–66093 tests 300 additional normal programs; 66095 reaches the budget cap.

**Inferred — crux.** No successful construction observed.

**Inferred — commitment.** Initially chose an unwritable work directory; random search did not find a qualifying program.

**Inferred — recovery.** Recovered directory choice; no witness recovery observed before censoring.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### glm-5p3 · replicate 3 · excluded: transport_or_incomplete_stream

Raw trial: `typecheck-soundness-witness__YYktR9w`. Trajectory SHA-256: `0b5048d4e94b2c03ff9cc3fcae9913a6668fccc57fafa9da3c65cb08dfe48c4c`.

**Verified — events.** 47–94 reads the specification and implementations; 47403 records a transport timeout with its reservation retained. No submitted construction appears.

**Inferred — crux.** Unknown from the bounded action windows.

**Inferred — commitment.** No candidate observed.

**Inferred — recovery.** Unobserved before transport interruption.

**Mechanism judgment.** Verified: final result is censored (ProxyTransportFailure); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### kimi-k3 · replicate 1 · reward 1.0

Raw trial: `typecheck-soundness-witness__wuCtLjL`. Trajectory SHA-256: `4b5cf172ad7b0234b2b19a41d027e099e72105d63e9903e9f32806656a197b83`.

**Verified — events.** 38–106 reads language, checker and interpreter; 22865 rereads checker; 23759–23760 writes a program and observes acceptance/type_error; 24084–24085 independently calls check/run and confirms error at interpreter step 50; 24580 explains the omitted nested write sets.

**Inferred — crux.** yes

**Inferred — commitment.** No failed candidate is observed. The successful construction makes nested effects grow across loop iterations while their memo signature stays constant.

**Inferred — recovery.** No concrete failed-candidate recovery was required.

**Mechanism judgment.** Inferred: direct success at the intended crux refutes a strong claim that this model cannot track the missing nested effects. It also demonstrates acceptance of a materially different correct program.

### kimi-k3 · replicate 2 · excluded: transport_or_incomplete_stream

Raw trial: `typecheck-soundness-witness__rKDuZdk`. Trajectory SHA-256: `2dded03f9150f01d4aca65610c27e82c27fead997df159c14f6fd8adff6a77b7`.

**Verified — events.** 42–148 reads the task files and starter program in six terminal calls; 26673 records ProxyTransportFailure TimeoutError with the reservation retained. No candidate program is recorded.

**Inferred — crux.** Unknown: no completed construction or terminal validation observed.

**Inferred — commitment.** No submitted wrong candidate observed.

**Inferred — recovery.** No recovery observed before the transport interruption.

**Mechanism judgment.** Verified transport censoring; no semantic failure evidence.

### kimi-k3 · replicate 3 · reward 1.0

Raw trial: `typecheck-soundness-witness__CMS53kv`. Trajectory SHA-256: `e3a063d0296b1afcc7f6db39ea7a104c6882896fab647655660af8dfde73b434`.

**Verified — events.** 16131–16132 constructs a program; 16647–16648 confirms checker True and type error at step 26, 401 bytes; 17271 explains nested write signatures; 17272 finishes.

**Inferred — crux.** Yes: memoized join hides a returned closure's cell write.

**Inferred — commitment.** No failed candidate observed.

**Inferred — recovery.** No recovery needed.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### kimi-k3 · replicate 4 · excluded: transport_or_incomplete_stream

Raw trial: `typecheck-soundness-witness__BG3PsRv`. Trajectory SHA-256: `2a1f7442a18472605bf141d65aa3d80259b4c1c3ebc7e0a16c679cbdb4541686`.

**Verified — events.** 35–92 reads specification and source; 27791 records a transport timeout with reservation retained.

**Inferred — crux.** Unknown: no completed construction.

**Inferred — commitment.** No candidate observed.

**Inferred — recovery.** Unobserved.

**Mechanism judgment.** Verified: final result is censored (ProxyTransportFailure); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### kimi-k3 · replicate 5 · excluded: budget_limit

Raw trial: `typecheck-soundness-witness__hj7NJa7`. Trajectory SHA-256: `727e4b28764f885a57eef63386433f8a0aa27785036621b1ed600f9fd113d6fb`.

**Verified — events.** 40–134 reads the implementations; 26489–26492 checks the starter and static-error behavior; 28258–28259 rejects an exploratory program; 32303–33079 fixes malformed AST, yielding an accepted normal program; 39067–39068 generates 200000 programs with 103152 accepted and no type error; 46435–46436 generates 300000 more with 5931 accepted and no type error; 46438 reaches budget cap.

**Inferred — crux.** No qualifying construction observed; exact crux understanding remains unknown in the reviewed windows.

**Inferred — commitment.** Early experiments were statically rejected, malformed, or accepted but normal; random searches did not find a witness.

**Inferred — recovery.** Recovered malformed AST, but no qualifying program before budget censoring.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

## exact-fused-dot

**Verified:** All three DeepSeek attempts pass the grader. Kimi and GLM attempts end at budget limits; their final correctness is unobserved. Several implement exact accumulation and recover errors in their own Fraction references or hand encodings. GLM replicate 2 repairs an actual negative-shift error (30578–31824). **Inferred:** Arithmetic bookkeeping and independent-reference construction cause friction, but no uncensored semantic failure supports frontier hardness. All Kimi/GLM denominators being zero makes transfer especially weak and the censoring informative.

### deepseek-v4p1-flash · replicate 1 · reward 1.0

Raw trial: `exact-fused-dot__94CNsPe`. Trajectory SHA-256: `0d90d32d2c2b581772847dff3212ab50f3219f26b9a8141deeb96f364bfa3773`.

**Verified — events.** 51–85 inspects public contract/examples; 19771–19772 writes an integer/dyadic solver and passes public smoke; 26534 builds a Fraction reference; 27300 observes a test helper name error; 27389–27390 observes sign mismatches; 28485–28741 isolates the reference sign error; 29371–29372 fixes the reference and observes zero mismatches; 32174–33511 checks special values and the overflow boundary; 38180–38181 observes 20,000 responses in 0.83 s; 42485–42486 has a recoverable test timeout; 42979–42980 caches enumeration and completes 512,000 brute checks; 45099–45100 checks overflow; 48936–48937 repeats the suites; final Harbor reward is 1.

**Inferred — crux.** yes: exact dyadic accumulation, one final rounding, signed zeros and flags are represented explicitly

**Inferred — commitment.** The first auxiliary Fraction decoder omits the finite sign, so its differential test reports false mismatches. A test helper also initially calls the wrong reference function name. Neither error is treated as a grader failure.

**Inferred — recovery.** Yes. The agent localizes and fixes its own reference sign error, then uses representable-value enumeration as another check. It also recovers after a 30-second tool timeout by caching the enumeration.

**Mechanism judgment.** Inferred: successful exact implementation and recovery refute this attempt as evidence for the rounded-intermediate failure hypothesis. The substantial self-testing is real agent work; the reported internal test counts are observations of tool output, not an independent certification of those tests.

### deepseek-v4p1-flash · replicate 2 · reward 1.0

Raw trial: `exact-fused-dot__6mpWfJp`. Trajectory SHA-256: `e7c002936e83fa0dee967c181c93e2fe60e450d1b79ae0e41c02408a0b396961`.

**Verified — events.** 21642–21643 implements exact solver and passes smoke; 28068–28069 revises exceptional handling; 33102–33103 reference comparisons have zero mismatches; 60234–60235 exhaustive small-format single pairs pass; 70499–70500 validates 20000 responses; 78302–78303 final smoke passes; 80262 finishes.

**Inferred — crux.** Yes: exact accumulation, rounding and exceptional values.

**Inferred — commitment.** Exceptional handling was revised after initial smoke; no failing candidate counterexample is observed in the bounded windows.

**Inferred — recovery.** Verified final success.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### deepseek-v4p1-flash · replicate 3 · reward 1.0

Raw trial: `exact-fused-dot__7shbQp8`. Trajectory SHA-256: `5c4e3a240f1a2c844518dc6116a558d42574b2951f71b1f964d766049e32a2e8`.

**Verified — events.** 15455–22117 implements/revises solver and passes smoke; 26818–27985 repairs reference treatment of exactly representable values, all 32000 checks pass; 29511–29664 handles overflow in the auxiliary float oracle; 35200–36369 corrects exception-oracle flags; 43425–43426 corrects a negative-tiny RUP hand expectation; 43942–43943 all final checks pass; 44557 finishes.

**Inferred — crux.** Yes: exact Fraction accumulation and rounding.

**Inferred — commitment.** Several auxiliary reference and hand-case expectations were wrong.

**Inferred — recovery.** Verified: corrected tests pass and grader gives reward 1.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### glm-5p3 · replicate 1 · excluded: budget_limit

Raw trial: `exact-fused-dot__dovg6kb`. Trajectory SHA-256: `e00796ff004b6df6155a9e61ae1c4db87af72322fbdebeb3fab273ed06c2ab3b`.

**Verified — events.** 45–82 reads public files; 33499–33500 probes float overflow; 35405–35406 writes an integer solver and passes public smoke; 38417 writes a Fraction reference; 40420 observes a float/numerator error; 40843 observes a reference assertion error; 41354 repairs reference log2; 45938–52216 revises hand expectations and obtains zero hand failures plus a public-smoke pass; 54506–54507 random comparison stops on a Fraction/float OverflowError; 54509 is ProxyBudgetExceeded before the next request.

**Inferred — crux.** yes: the candidate explicitly uses integer accumulation and final rounding; own verification covers boundaries but repeatedly needs repair

**Inferred — commitment.** The auxiliary reference introduces float values through powers of two, and several hand-authored expected values need revision. These are observed self-test problems, not a verified hidden-grader failure of the submitted solver.

**Inferred — recovery.** Partially. It fixes the zero-sign/reference-log2 checks and hand cases, but its random reference still errors when the conservative per-trial reservation limit ends the attempt.

**Mechanism judgment.** Inferred: verification difficulty is visible, but the final outcome is budget-censored. No semantic failure or success is counted; the valid denominator remains zero for this family/task until another uncensored attempt completes.

### glm-5p3 · replicate 2 · excluded: budget_limit

Raw trial: `exact-fused-dot__nt8BKWV`. Trajectory SHA-256: `800b7058f28b7ebb6ec418ebdfc04a4bb88364d0397268a054390568c608c558`.

**Verified — events.** 23015–23016 implements solver and passes smoke; 28269–30578 uncovers errors in auxiliary reference and a candidate negative shift; 31823–31824 repairs candidate shift; 34825–34826 binary64 checks pass; 40545–40546 isolates 11279 reference flag mismatches with identical bits; 42492–42493 extends reference exponent grid; 42495 reaches budget cap.

**Inferred — crux.** Yes: integer encoding and overflow flags.

**Inferred — commitment.** Candidate used a left shift with a possibly negative count; auxiliary reference also mishandled overflow flags.

**Inferred — recovery.** Candidate shift repaired; final reference repair is unvalidated before censoring.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### glm-5p3 · replicate 3 · excluded: budget_limit

Raw trial: `exact-fused-dot__arxzZuE`. Trajectory SHA-256: `24b21aa3ca782d66fcd76a3a45574c2e8549da1e44dca0812b67ba473ca0541c`.

**Verified — events.** 22562–22563 implements solver and passes smoke; 28333–28334 passes 40000 reference comparisons; 30150–30151 binary64 products match; 33088–38872 repeatedly adjusts boundary expectations; 40745–40746 boundary checks pass; 42626–42627 passes 45000 further comparisons; 42953–42954 smoke passes; 42956 reaches budget cap.

**Inferred — crux.** Yes: exact rounding and boundary semantics.

**Inferred — commitment.** Several hand boundary expectations were incorrect; no unresolved candidate bug established.

**Inferred — recovery.** Verified corrected comparisons; final completion censored.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### kimi-k3 · replicate 1 · excluded: budget_limit

Raw trial: `exact-fused-dot__4RRbnGP`. Trajectory SHA-256: `7fe006e14f50387b7d3d21fcb2e10ac608296e2bb004bd896f20a07c087b214b`.

**Verified — events.** 21854–21909 inspects public files; 22379–22380 decodes the cancellation example; 24094–24095 writes an exact integer accumulator and passes public smoke; 27884 builds a Fraction reference; 28615–28616 toy/random comparisons report zero mismatches; 29559–29560 binary64 comparisons report zero mismatches; 38594–38595 hand tests report eight mismatches; 40537–40538 recomputes the disputed encodings with Fractions; 40540 is ProxyBudgetExceeded before another request.

**Inferred — crux.** yes: inspected solver retains exact integer products, handles one final rounding and tininess after rounding

**Inferred — commitment.** The hand-authored special-case expectations use incorrect encodings/magnitudes; for example, (ebits=3, fbits=3) 07*18 is 7/32, which the candidate returns exactly. This differs from the agent's expected inexact rounded value. No hidden-grader failure is observed.

**Inferred — recovery.** Partially. Existing differential suites succeed and the last tool computation identifies bad hand expectations, but the reservation cap prevents observing a clean final response.

**Mechanism judgment.** Inferred: the trajectory reaches the arithmetic crux and exposes self-verification errors. Because it is budget-censored, it establishes neither a counted task failure nor a counted success.

### kimi-k3 · replicate 2 · excluded: budget_limit

Raw trial: `exact-fused-dot__qjzc947`. Trajectory SHA-256: `77c6505526e84f3a734f9edfe28d7ab7da9bf84cf82de4063b545794762082b1`.

**Verified — events.** 29945–29946 implements exact solver and passes smoke; 34794–34795 exhaustive/curated/random comparisons report zero failures; 36612–36613 float-format comparisons report zero failures; 43046–43047 three hand expectations disagree; 43049 reaches budget cap.

**Inferred — crux.** Yes: exact arithmetic and rounding.

**Inferred — commitment.** Three hand-test disagreements remain unresolved in this trajectory.

**Inferred — recovery.** Unknown for the final hand disagreements; no final grader result.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### kimi-k3 · replicate 3 · excluded: budget_limit

Raw trial: `exact-fused-dot__dkWQBQe`. Trajectory SHA-256: `ba5ade30717b24986da7e1132edd806626c841e1ac9912e6ede54a39fab5ce60`.

**Verified — events.** 28663–28664 implements solver and passes smoke; 32593–32594 passes 30000 random comparisons; 33309–33310 exhaustive small-format checks pass; 34742–34743 binary64 comparisons pass; 36720–37724 corrects an all-negative-zero test whose products had mixed signs; 39998–39999 exact-shift check passes; 40001 reaches budget cap.

**Inferred — crux.** Yes: exact accumulation and zero/tie semantics.

**Inferred — commitment.** An auxiliary signed-zero expectation ignored a product sign.

**Inferred — recovery.** Verified: corrected edge tests pass; final completion censored.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### kimi-k3 · replicate 4 · excluded: budget_limit

Raw trial: `exact-fused-dot__mavgxJ8`. Trajectory SHA-256: `9757d715163070dd4c5fb45d4ce119711776b4390bf8090303e99e8efe47fd97`.

**Verified — events.** 28243–28244 implements solver and passes smoke; 36386–39892 corrects hand encodings and passes 60000 comparisons; 41780–42639 corrects lost sign in binary64 reference and passes two comparison batches; 42641 reaches budget cap.

**Inferred — crux.** Yes: exact products and single rounding.

**Inferred — commitment.** Auxiliary hand encodings and reference sign were wrong.

**Inferred — recovery.** Verified: corrected references pass; final completion censored.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### kimi-k3 · replicate 5 · excluded: budget_limit

Raw trial: `exact-fused-dot__mA2apgy`. Trajectory SHA-256: `1cd88b93dcf0714219904b2db068d87fbd441c556d0bd2019de6302645e4ce6e`.

**Verified — events.** 29345–29346 implements exact solver and passes smoke; 37484–37485 has 11 hand-test disagreements; 41237–41238 attempted expected-value edits fail; 44124–44125 rewrites tests, leaving one infinity/zero-product expectation disagreement; 44127 reaches budget cap.

**Inferred — crux.** Yes: exact arithmetic implemented; exceptional-test interpretation incomplete.

**Inferred — commitment.** Hand-case encodings/expectations were repeatedly revised; the last disagreement remains unresolved in the recorded run.

**Inferred — recovery.** Partial recovery from 11 disagreements to one; no final grader result.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

## mixed-width-tso

**Verified:** Successful attempts construct complete state searches with byte forwarding, FIFO drains, fences and exchanges. DeepSeek replicate 2 repairs sibling-transition memory contamination (8243–9557), then ends in a terminal harness timeout. Other successful attempts recover malformed test requests/reference representations. **Inferred:** The intended machine-state mechanism is repeatedly handled, weakening hardness. Two outer terminal timeouts are excluded; a process-group interaction with nested timeout commands is plausible but not independently reproduced.

### deepseek-v4p1-flash · replicate 1 · excluded: terminal_harness_timeout

Raw trial: `mixed-width-tso__ewcVoqu`. Trajectory SHA-256: `5430517eb2582e4404fde162bf47d7671c63252dc110efb4c10429c415d43c3b`.

**Verified — events.** 47–83 reads public files; 3728–3729 writes DFS state enumeration and passes smoke; 4389–4390 runs 200 generated requests; 5419–5420 checks store/load stress cases; 6170–6171 searches for larger states; 7290–7291 receives a recoverable timeout; command 7930 starts another search, but 7931 records RuntimeError: Command timed out after 40 seconds with no terminal result. Harbor traceback points to the outer Docker exec call.

**Inferred — crux.** yes: implements the finite-state search and tests larger states, but no completed final response/grade is observed

**Inferred — commitment.** It extends performance searches after fast public/stress cases. No concrete semantic error in the candidate is established.

**Inferred — recovery.** After the first ordinary tool timeout it revises its search. The next command hits the outer Docker exec timeout, which terminates the agent instead of returning a recoverable result.

**Mechanism judgment.** Inferred: terminal harness censoring; root cause of the outer timeout is unknown. Exclude from difficulty evidence. The runtime exception is not counted as a memory-model failure, and no replacement attempt is silently added. The final command embeds a 60-second GNU timeout while the terminal request allows 30 seconds; inferred possible cause is a nested process group surviving the wrapper timeout. This cause was not experimentally reproduced, so the root cause remains unverified.

### deepseek-v4p1-flash · replicate 2 · excluded: terminal_harness_timeout

Raw trial: `mixed-width-tso__cBqSDsE`. Trajectory SHA-256: `43dac0f928f2a0e6e06a3ae4cf095d2fc00ec2f248833f6eb4afd739c3bb24a2`.

**Verified — events.** 4898–4899 implements state exploration and passes smoke; 5941–6107 fixes random generator widths; 7106–7107 reports differential mismatches; 8243–8244 repairs the exchange transition to avoid mutating shared memory for later sibling transitions; 9556–9557 passes 3752 comparisons and 9973–9974 passes 1500 larger comparisons; 10869 records a recoverable command timeout; 11795 starts nested timeout 55 with a 30-second tool allowance; 11796 records outer 40-second execution timeout.

**Inferred — crux.** yes

**Inferred — commitment.** Exchange assigned to the parent memory variable, contaminating sibling transitions.

**Inferred — recovery.** Verified: repair followed by two zero-mismatch comparison batches. Final completion is unobserved after harness timeout.

**Mechanism judgment.** Inferred: a real implementation error was recovered. The ending is a harness censor, not a semantic failure; nested timeout process-group behavior remains an unconfirmed explanation.

### deepseek-v4p1-flash · replicate 3 · reward 1.0

Raw trial: `mixed-width-tso__iCifsHA`. Trajectory SHA-256: `282919be9f222d58c69d7d0536a640dcd5666be43038a5c591c54f101f6d3557`.

**Verified — events.** 33643–33644 passes 4000 tiny naive comparisons; 36636–36637 writes final solver and repeats comparisons; 36761–36762 completes 5000 and 20000 request batches; 38003–38004 passes 4000 comparisons against a core-memo alternative; 38179–38180 smoke passes; 38669 finishes. Earlier visible stress searches returned recoverable timeout results.

**Inferred — crux.** Yes: exhaustive state semantics and final outcomes.

**Inferred — commitment.** No unresolved candidate error is established in the reviewed windows.

**Inferred — recovery.** Verified final success despite recoverable stress-search timeouts.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### glm-5p3 · replicate 1 · reward 1.0

Raw trial: `mixed-width-tso__cPQEdk2`. Trajectory SHA-256: `b368adc78b81e304d572e9eb5d500d9770589a8aa67249d1693b0917fad24312`.

**Verified — events.** 42–72 inspects public files; 4174–4175 writes BFS over (program counters, FIFO buffers, memory, observations) and passes smoke; 5097–5098 checks overlapping stores, per-byte forwarding, exchanges and fences; 5568–5569 runs larger examples; 5996 gives final explanation; Harbor reward is 1.

**Inferred — crux.** yes: candidate code searches newest buffered writes separately for each load byte, drains oldest stores, waits on only the issuing buffer, and requires empty buffers at termination

**Inferred — commitment.** No failed candidate or concrete wrong semantic commitment is observed.

**Inferred — recovery.** No failed-candidate recovery is observed; the first implementation succeeds.

**Mechanism judgment.** Inferred: a direct complete-state solution refutes the proposed omitted-transition mechanism for this attempt and supports treating this task as a control.

### glm-5p3 · replicate 2 · reward 1.0

Raw trial: `mixed-width-tso__ixyHTp3`. Trajectory SHA-256: `b224cc0a29e017db3cb111090e0f5e3eca90a3cdb093a887af42d5f4a8aaad01`.

**Verified — events.** 1675–1676 implements full-state exploration and passes public smoke; 2065–2393 fixes auxiliary syntax; 2922–3594 investigates empty outcomes from malformed thread nesting; 4336–4337 fixes the test requests and observes expected outcomes; 4943–5439 stress cases complete; 5584–5585 smoke passes; 5819 finishes.

**Inferred — crux.** yes

**Inferred — commitment.** Malformed auxiliary requests omitted a level of thread nesting, creating empty outcomes. No main solver revision is observed.

**Inferred — recovery.** Verified: corrected request nesting gives the expected single-thread exchange and forwarding outcomes.

**Mechanism judgment.** Inferred: a complete implementation succeeds at the intended crux. Auxiliary test mistakes do not establish a task failure.

### glm-5p3 · replicate 3 · reward 1.0

Raw trial: `mixed-width-tso__UzBgYW4`. Trajectory SHA-256: `cd03265c1609fa89950d9d5d3a085b0d3d6cb8978e15ba779ed3ec87f059d3b3`.

**Verified — events.** 2806–2807 implements search and passes smoke; 3784–6111 auxiliary tests have bounds/import/generator errors and a recoverable timeout; 6535–6536 corrected random cross-check has zero differences; 16672–18870 fixes stress-script syntax; 23218–23219 final implementation passes structured tests; 24486–24487 exchange case matches expectation; 24606–24607 final smoke/syntax pass; 25078 finishes.

**Inferred — crux.** Yes: complete search with byte forwarding and exchanges.

**Inferred — commitment.** Auxiliary tests included invalid bounds, missing imports, malformed scripts and representation comparisons.

**Inferred — recovery.** Verified: repaired checks and final grader pass; intermediate timeouts were recoverable.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### kimi-k3 · replicate 1 · reward 1.0

Raw trial: `mixed-width-tso__88KyvAr`. Trajectory SHA-256: `a72c4ad5ad070929832c09a73276c8bb604e81aa99b8b2fb630cc0814901cbbb`.

**Verified — events.** 70–118 inspects public files; 9984–9985 writes the state search and passes smoke; 12426–12427 auxiliary reference returns no outcomes; 12709–12710 fixes its instruction indexing and reports 2,000 matching cases; 12844–12845 reports four further 1,500-case batches; 13762–13763 checks large examples; 16187 observes a helper import error; 16377–16378 extracts the helper and completes larger-state checks; 17996–17997 checks edge cases and a 300-request batch; 18413–18414 repeats smoke and 500 comparisons; Harbor reward is 1.

**Inferred — crux.** yes: enumerates instruction and FIFO-drain transitions, includes pending buffers and observations in the state, and tests partial forwarding and drain-after-finish

**Inferred — commitment.** The first auxiliary reference fetches a thread program instead of the next instruction, yielding an empty expected set. A later test helper executes argument-dependent code during import. No observed candidate semantic defect survives these checks.

**Inferred — recovery.** Yes: repairs both auxiliary testing errors, checks outcome-set agreement under several seeds, and finishes successfully.

**Mechanism judgment.** Inferred: complete search and deliberate semantic checks weaken the intended transition-omission hypothesis. The bounds allow fast enumeration, consistent with the control role.

### kimi-k3 · replicate 2 · reward 1.0

Raw trial: `mixed-width-tso__MX2PDSY`. Trajectory SHA-256: `27b8f32119a5aabbc277ac2b9d2fbd935277a302dcbba40c239e9582c778f74b`.

**Verified — events.** 5678–5679 implements full-state search and passes smoke; 7069–7070 passes 400 small comparisons; 9524–9525 has a recoverable stress timeout; 10894–12679 rewrites an incomplete alternative reference and reports zero mismatches; 14168–14169 structured checks pass; 14901–14902 final smoke passes; 15412 finishes.

**Inferred — crux.** Yes: full buffered-machine outcomes.

**Inferred — commitment.** Auxiliary alternative reference needed a rewrite; a final optional batch file was missing.

**Inferred — recovery.** Verified: rewritten reference comparisons and final reward pass.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### kimi-k3 · replicate 3 · reward 1.0

Raw trial: `mixed-width-tso__ZKeswpq`. Trajectory SHA-256: `679c76ff1b748cc3fedd70deecaa2bc44d5f31dc525e9af31363a547c52a0b58`.

**Verified — events.** 8822–8823 implements search and passes smoke; 10140–10755 passes three 400-case comparison batches; 12581–12582 passes 1200 biased cases; 13278–13279 validates 300-response CLI batch; 13528–13529 final smoke passes; 13901 finishes.

**Inferred — crux.** Yes: exact outcomes including exchange and drains.

**Inferred — commitment.** No failed candidate observed.

**Inferred — recovery.** No recovery needed.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### kimi-k3 · replicate 4 · reward 1.0

Raw trial: `mixed-width-tso__E9r9vnJ`. Trajectory SHA-256: `442ba16aaa5f505c632d48363a0944ff25d9f0134778f9a727273faa52390ea6`.

**Verified — events.** 8469–8470 implements solver and passes smoke; 9778–10521 fixes tuple unpacking and observation nesting in an auxiliary reference, then passes comparison batches; 13056–13057 passes 1500 biased cases; 13662–13956 fixes malformed test thread nesting and passes 404 CLI requests; 15122–15123 final smoke/syntax pass; 15558 finishes.

**Inferred — crux.** Yes: byte forwarding and complete state exploration.

**Inferred — commitment.** Auxiliary reference and request nesting were wrong.

**Inferred — recovery.** Verified: corrected comparisons and CLI checks pass.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### kimi-k3 · replicate 5 · reward 1.0

Raw trial: `mixed-width-tso__t39RSQx`. Trajectory SHA-256: `db2eef5bd0f069e2c0138dae1726b4c5560c2da5e409cf880d4d47e3d5fc1063`.

**Verified — events.** 7784–7785 implements solver and passes smoke; 9819–9820 differential check reports zero mismatches; 10544–10903 tests forwarding, exchange and empty threads; 11484 finishes.

**Inferred — crux.** Yes: machine transitions and complete outcome search.

**Inferred — commitment.** No failed candidate observed.

**Inferred — recovery.** No recovery needed.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

## checkpointed-journal

**Verified:** Every scheduled attempt finishes with reward 1. Implementations compose prefix validation, transaction incarnations, commit seals and checkpoint replay. Many apparent intermediate failures come from auxiliary ASCII/hex or record-length expectations; they are corrected without changing the main solver. **Inferred:** This is a valid control with little present evidence of frontier difficulty. Auxiliary mistakes alone do not confirm the intended lifecycle-state failure mechanism.

### deepseek-v4p1-flash · replicate 1 · reward 1.0

Raw trial: `checkpointed-journal__Vp3S5Cs`. Trajectory SHA-256: `cff06cf151eda7b22ff595101cd92322c0ec0ef3710ab2b9ed70aa823ba0442a`.

**Verified — events.** 47–89 reads public files; 3589–3590 writes replay and passes smoke; 5532–5533 constructs record/seal/prefix cases; 7613–7614 compares against its separate reference and outputs all ok; 7960–7961 repeats smoke and empty-log cases; 8248 explains transaction incarnations, seals and checkpoints; Harbor reward is 1.

**Inferred — crux.** yes: staged transaction state and valid-prefix replay, including seal verification and checkpoint behavior

**Inferred — commitment.** No failed candidate or concrete wrong replay commitment is observed.

**Inferred — recovery.** No failed-candidate recovery is observed; the first implementation succeeds.

**Mechanism judgment.** Inferred: successful concrete replay and independent self-checking weaken the delayed-recovery-error hypothesis for this attempt. The final response claims 20,000 internal differential cases; tool output confirms all ok, not an independent audit of their coverage.

### deepseek-v4p1-flash · replicate 2 · reward 1.0

Raw trial: `checkpointed-journal__2omdLHC`. Trajectory SHA-256: `442cd33b4a2f9907946829c03c6336a9bb93f5c9280959ec96aad822968905e8`.

**Verified — events.** 770–1014 decodes record and seal CRCs; 7424–7425 implements staged replay and passes smoke; 10299–10300 sees checkpoint test mismatches; 10931–10932 corrects the expected results and passes 27 checks; 13625–13626 reports zero mismatches on 4000 generated cases; 15121–15122 completes 2000 requests; 15754–15755 final smoke passes; 16108 finishes.

**Inferred — crux.** yes

**Inferred — commitment.** An auxiliary test incorrectly expected no replay for a commit above the checkpoint.

**Inferred — recovery.** Verified: corrected auxiliary expectations pass; the main implementation retains replay gating by commit sequence.

**Mechanism judgment.** Inferred: a complete implementation succeeds at the intended crux. Auxiliary test mistakes do not establish a task failure.

### deepseek-v4p1-flash · replicate 3 · reward 1.0

Raw trial: `checkpointed-journal__C2UE2RX`. Trajectory SHA-256: `edb9aa0208be08c8ee252d23268a32b62603c8031c77139d6fc741fc1dee5e1c`.

**Verified — events.** 3503–3504 implements replay and passes smoke; 5833–6348 repairs auxiliary prefix-byte expectations and passes 15 tests; 8588–8589 completes 300 generated requests; 9491–9492 final smoke and edge checks pass; 9822 finishes.

**Inferred — crux.** Yes: prefix parsing and staged replay.

**Inferred — commitment.** Auxiliary prefix-byte expectations were incorrect.

**Inferred — recovery.** Verified: repaired tests and final reward pass.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### glm-5p3 · replicate 1 · reward 1.0

Raw trial: `checkpointed-journal__DFMU8Hr`. Trajectory SHA-256: `a6e2df1b17e96101ce39e15ce8ebcc02e907d871a9ff25efb9c5a45cd67888fc`.

**Verified — events.** 41–83 reads public files; 2473–2474 writes replay and passes smoke; 5291–5292 wrong checkpoint expectation fails; 5481–5482 another overlapping-patch expectation fails; 5743 records a hex helper error; 5839–6489 fixes malformed-record and page-length assertions, then all edge tests pass; 7347–7348 performance input stops early at a record invalid under the page bounds; 8072–8073 rebuilds a long valid log and reports correct applied pages; 8251–8252 repeats smoke/uppercase-hex case; Harbor reward is 1.

**Inferred — crux.** yes: candidate separates record validation, staged transaction state, seal validation and checkpoint application

**Inferred — commitment.** Several hand expectations confuse checkpoint position, overlapping commits, invalid patch bounds or hex length. These are errors in agent-authored tests; main.py is not edited after the initial successful implementation.

**Inferred — recovery.** Yes: revises the test expectations/helpers, then constructs a valid large log and finishes with passing checks.

**Mechanism judgment.** Inferred: the agent succeeds at the intended lifecycle rules. Observed self-test errors do not support counting a delayed replay failure, and the clean Harbor result is positive evidence.

### glm-5p3 · replicate 2 · reward 1.0

Raw trial: `checkpointed-journal__WdhY68X`. Trajectory SHA-256: `d0a26487afab5ea62a7bc500743df2e6aa8d4e1ee8dfda66eacb3bde70178739`.

**Verified — events.** 2661–2662 implements replay and passes smoke; 6717–7210 auxiliary tests have bytes/string serialization errors and bad expected values; 13184–13456 repairs generator lengths and page expectations, leaving a reverse-commit expectation mismatch; 13729–13730 corrects that expectation and all selftests plus smoke pass; 14112–14113 checks empty log and input; 14543 finishes.

**Inferred — crux.** yes

**Inferred — commitment.** Auxiliary expectations incorrectly handled commit ordering and page sizes; no main implementation repair is recorded.

**Inferred — recovery.** Verified: final corrected selftests and smoke pass.

**Mechanism judgment.** Inferred: complete replay handles the intended interactions; recovered test errors do not support the proposed task failure mechanism.

### glm-5p3 · replicate 3 · reward 1.0

Raw trial: `checkpointed-journal__EkPvATz`. Trajectory SHA-256: `b830d9baaf188617050442fc8010235a2e3e1b04d4b00d823c3ca85623519eef`.

**Verified — events.** 2282–2283 implements replay and passes smoke; 4510–11887 auxiliary tests repeatedly confuse ASCII with hex bytes, record lengths, payload bounds and image sizes; 16033–16034 confirms computed image and prefix; 20289–20441 corrects a page-length comparison and all final tests pass; 21063 finishes.

**Inferred — crux.** Yes: commit order, prefix validation and checkpoint replay.

**Inferred — commitment.** Repeated auxiliary-test encoding and length errors; no main solver revision recorded.

**Inferred — recovery.** Verified: corrected final tests and hidden grader pass.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### kimi-k3 · replicate 1 · reward 1.0

Raw trial: `checkpointed-journal__eKbK6XP`. Trajectory SHA-256: `6665fe60894d9d92de97050c949c43c6728c2b12ad2c47fe2bb20f3666c7676d`.

**Verified — events.** 5864–5942 inspects runtime/public files; 6872–6873 decodes a real example and checks its CRC/seal; 8134–8135 writes replay and passes smoke; 14442–14443 targeted checks expose a one-byte mistake in its expected valid_bytes; 14639–14640 corrects that expectation; 17675–18647 two-phase reference comparisons report 44,000 matching generated cases across four seeds; 18648–18649 verifies a 300-line subprocess batch; 19473–19474 stresses dense logs; 20403–20404 adds 10,000 comparisons and repeats smoke; Harbor reward is 1.

**Inferred — crux.** yes: explicitly validates records below the checkpoint, retains incarnation state, validates seals and applies only eligible committed patches

**Inferred — commitment.** A hand test incorrectly adds 26 bytes for a 25-byte patch record. The implementation returns the correct 67-byte valid prefix.

**Inferred — recovery.** Yes: fixes the expected byte count and completes several reference comparisons and final checks.

**Mechanism judgment.** Inferred: strong success at staged recovery rules weakens the intended delayed-consequence mechanism for this attempt. Internal fuzz counts are observed tool output, not independently audited coverage.

### kimi-k3 · replicate 2 · reward 1.0

Raw trial: `checkpointed-journal__GcyBMiW`. Trajectory SHA-256: `16dc8fbecd696f5e9f924b8d37220c587f177ae23461c422cab0bc0efde62280`.

**Verified — events.** 5751–5752 implements replay and passes smoke; 9413–9414 has a checkpoint-image test using a nonempty log; 9594–9595 corrects that test and all 41 pass; 11875–11876 reports 4000 zero-mismatch comparisons; 13968–13969 final edge checks and smoke pass; 14565 finishes.

**Inferred — crux.** Yes: staged replay, commit seals and checkpoint.

**Inferred — commitment.** An auxiliary empty-log expectation accidentally reused a nonempty log.

**Inferred — recovery.** Verified: fixed test passes; no solver repair needed.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### kimi-k3 · replicate 3 · reward 1.0

Raw trial: `checkpointed-journal__knZc99M`. Trajectory SHA-256: `5e00414045b5ab6d2a2efa01b1fd7ea15d68edf3b7295a98da7c11915cbcb627`.

**Verified — events.** 11577–11578 implements replay and passes smoke; 15930–16702 corrects two auxiliary tests, all 35 pass; 18563–19664 comparison batches have zero mismatches; 19665–20694 corrects close/reopen test construction; 23390–23391 checkpoint closure cases pass; 23571–23572 final smoke and further comparisons pass; 24174 finishes.

**Inferred — crux.** Yes: transaction incarnations, seals and checkpoint.

**Inferred — commitment.** Some auxiliary logs and expected prefixes were incorrectly constructed.

**Inferred — recovery.** Verified: corrected logs pass; main replay remains unchanged.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### kimi-k3 · replicate 4 · reward 1.0

Raw trial: `checkpointed-journal__Z9YpHsu`. Trajectory SHA-256: `700558fa0dfa000c35015c960ec15f5f2083800a9f19865755a427ccf2815100`.

**Verified — events.** 5254–5255 implements replay and passes smoke; 9242–10200 corrects four targeted-test expectations, all 46 pass; 12582–12583 matches 600 generated cases; 13314–14361 corrects maximum-log construction and completes 1000 requests; 15139–15140 repeats smoke and checks; 15630 finishes.

**Inferred — crux.** Yes: full replay interactions.

**Inferred — commitment.** Targeted test expectations and one stress log were incorrect.

**Inferred — recovery.** Verified: corrected tests and final grader pass.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### kimi-k3 · replicate 5 · reward 1.0

Raw trial: `checkpointed-journal__nYcKYYm`. Trajectory SHA-256: `a49a93d5972da19ac70c1fbb090b9a2194c7aaee215ea24caa99413597d6e660`.

**Verified — events.** 13398–13399 implements replay and passes smoke; 17305–18229 corrects several hand-computed byte counts; 20008–20009 matches 4000 generated cases; 21200–21201 processes 300 large logs; 22258–23227 repairs an extreme-sequence expectation; 23472–23473 final tests pass; 23929 finishes.

**Inferred — crux.** Yes: byte-prefix validation and transaction lifecycle.

**Inferred — commitment.** Auxiliary record-byte counts and an extreme-sequence expectation were wrong.

**Inferred — recovery.** Verified: corrected hand cases, comparisons and final reward pass.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

## atomic-range-history

**Verified:** Completed GLM and DeepSeek attempts pass via finite order search. Some censored attempts identify and recover real candidate errors: DeepSeek replicate 1 corrects false-CAS reachability (60367–64428), and Kimi replicate 5 rewrites a candidate after 49 differential mismatches (12272–16442). Many attempts spend further work on performance hunts before budget or harness interruption. **Inferred:** The 10-transaction bound makes exhaustive search feasible; observed recovery weakens a strong incomplete-search hypothesis. Unresolved auxiliary assertions and censored artifacts are not counted as semantic failures.

### deepseek-v4p1-flash · replicate 1 · excluded: budget_limit

Raw trial: `atomic-range-history__Jcc8PCj`. Trajectory SHA-256: `7272d9830da0c04b058f9f9e57a180fc230ce6c12d606993263dcf61ee60ea1c`.

**Verified — events.** 18854–18855 implements search and passes smoke; 60366–60367 permutation comparison finds a false negative at seed 184; 61461–61462 reproduces it; 64336–64337 repairs the false-CAS write-set reachability pruning; 64427–64428 and 64762–64763 pass 5000 and 2000 comparisons; 71827–71828 adds compact encoding and passes smoke plus 5000 comparisons; 71830 reaches the per-trial budget cap.

**Inferred — crux.** yes

**Inferred — commitment.** The first reachability pruning incorrectly treated the new CAS value as written when the expected CAS result was false.

**Inferred — recovery.** Verified: the recorded counterexample returns a valid order after the repair, followed by successful differential comparisons.

**Mechanism judgment.** Inferred: a real candidate error was found and recovered. The final trial is budget-censored; neither final success nor semantic failure is observed.

### deepseek-v4p1-flash · replicate 2 · reward 1.0

Raw trial: `atomic-range-history__AkwcFJ8`. Trajectory SHA-256: `83c089ec5d291bb53d0a57c7ecd9b3b98375d6c7abdd7ab8da09eb35bf66e8fa`.

**Verified — events.** 5146–5147 implements search and passes smoke; 5913–5914 compares random histories without mismatch; 6475–9148 explores performance; 13233–13234 rewrites search with reachability pruning and repeats smoke/comparisons; 15393–15394 tests constructed satisfiable and mutated histories; 20678–20679 repeats differential checks; 22001–22255 validates orders on a 4000-request batch; 24679–24680 final smoke passes; 25085 finishes.

**Inferred — crux.** yes

**Inferred — commitment.** No failed candidate is observed. Performance checks motivate pruning.

**Inferred — recovery.** No demonstrated candidate-error recovery was needed.

**Mechanism judgment.** Inferred: exhaustive replay and safe pruning solve the finite search task, supporting its role as an easy control.

### deepseek-v4p1-flash · replicate 3 · excluded: terminal_harness_timeout

Raw trial: `atomic-range-history__vt9Mb5t`. Trajectory SHA-256: `17115595035e24aa94a1bab5a063a3c2375e6942581ddd8ed66c4a3fd835d6af`.

**Verified — events.** 5081–5082 implements search and passes smoke; 5995–5996 random comparisons have zero mismatches; 14803–14804 optimized solver passes tuple state to a dict-based feasibility routine; 16011–16012 repairs representation and smoke/comparisons pass; 20739–20740 a performance search has a recoverable timeout; 21689–21690 ends with outer 40-second terminal timeout.

**Inferred — crux.** Yes: replay search and reachability optimization.

**Inferred — commitment.** Optimization mixed tuple and dict representations.

**Inferred — recovery.** Verified repair before the final harness interruption; no final grader result.

**Mechanism judgment.** Verified: final result is censored (RuntimeError); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### glm-5p3 · replicate 1 · reward 1.0

Raw trial: `atomic-range-history__C9s8Puv`. Trajectory SHA-256: `75d709bd93eab9dbef9c9368fdd092ca13041deb734e491d05d17eefea0f5c67`.

**Verified — events.** 45–77 reads public files; 1974–1975 writes cached transaction replay/order search and passes smoke; 3516–3517 permutation comparison reports zero disagreements for three seeds; 4055–5031 runs larger unsatisfiable examples; 5839–5840 one hand-expected order disagrees with the returned order; 6282–6283 checks the actual order with valid_history, confirms the returned t1,t0 order is valid and the expected t0,t1 order is invalid, then reruns three seed batches and smoke; Harbor reward is 1.

**Inferred — crux.** yes: searches whole transactions, replays observations and enforces real-time predecessors

**Inferred — commitment.** An auxiliary edge case initially expects t0 before t1, although t1 must read the value before t0 deletes it. The solver returns the correct alternative order.

**Inferred — recovery.** Yes: verifies both orders directly against the public behavioral checker and recognizes the mistaken expected order.

**Mechanism judgment.** Inferred: success via complete finite search refutes the incomplete-order mechanism for this attempt. The test-error recovery also supports accepting materially valid orders rather than one reference ordering.

### glm-5p3 · replicate 2 · reward 1.0

Raw trial: `atomic-range-history__aKXNSSd`. Trajectory SHA-256: `b2582eb98c507b39bf1be1efbf831121ee174c8e555ae01b65b2c9554ec58409`.

**Verified — events.** 2583–3483 implements replay search and passes smoke; 5945–5946 passes fixed/random checks; 7753–10681 auxiliary stress scripts have repeated syntax/format errors; 11284–11285 corrects them; 14336–15910 resolves a parity assertion and validates 670 witnesses and 1330 nulls; 16120–16121 final smoke passes; 16617 finishes.

**Inferred — crux.** Yes: whole-transaction search and semantic replay.

**Inferred — commitment.** Repeated auxiliary stress-script syntax and formatting errors; the parity assertion's exact cause is not established here.

**Inferred — recovery.** Verified: corrected stress and parity checks pass, followed by reward 1.

**Mechanism judgment.** Inferred: valid success weakens the proposed hardness mechanism.

### glm-5p3 · replicate 3 · excluded: budget_limit

Raw trial: `atomic-range-history__WGWmXJ2`. Trajectory SHA-256: `31d1598fb50ba286184c3db9bf9d34f48b7592a2f93386624e603d09bc2405c7`.

**Verified — events.** 6076–6077 implements solver and passes smoke; 7690–9147 comparison reports six bad cases despite an initial repair; 10122–10123 changes memoization state and reports zero bad cases; 21660–21661 optimized solver repeats smoke/comparisons successfully; 33528–33529 stress hunt has recoverable timeout; 33531 reaches budget cap.

**Inferred — crux.** Yes: whole-state search and pruning.

**Inferred — commitment.** Initial memoization/pruning lost distinctions needed by the search; the precise causal distinction requires fuller code comparison.

**Inferred — recovery.** Verified: revised state handling and subsequent comparisons report zero bad cases; final completion censored.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### kimi-k3 · replicate 1 · excluded: terminal_harness_timeout

Raw trial: `atomic-range-history__At9Vdgx`. Trajectory SHA-256: `4734a985bda8d2536cfb84035d6239deb0556c40d7bd120a7bbe3a59829d2bc9`.

**Verified — events.** 10515–10516 implements cached replay search and passes smoke; 11620–11621 passes 4000 permutation comparisons; 14718–14819 fixes auxiliary test syntax; 16197–16198 brute force rejects a purported satisfiable generated case; 16805–16806 fixes generator intervals and passes 600 constructed cases plus 120 comparisons; 21626–22951 has unresolved auxiliary test assertions; 29542 starts a nested timeout command; 29543 raises outer Docker execution timeout after 40 seconds.

**Inferred — crux.** yes: implemented interval-constrained exhaustive replay

**Inferred — commitment.** Some auxiliary tests had incorrect syntax or inconsistent planted intervals. Later auxiliary assertions remain unresolved in the reviewed windows.

**Inferred — recovery.** Verified recovery of the syntax and interval-generator issues; unknown for the later assertions.

**Mechanism judgment.** Inferred: the final interruption is terminal harness noise. Nested timeout process-group behavior is a plausible cause, not a reproduced diagnosis. No final grader result is available.

### kimi-k3 · replicate 2 · excluded: budget_limit

Raw trial: `atomic-range-history__BEggeaB`. Trajectory SHA-256: `c0570f9bef31075656e12f9d4759ef7f2a73143b974a2f58642f306872687b09`.

**Verified — events.** 17984–17985 implements cached search and passes smoke; 19727–21041 comparisons report zero bad cases; 28982–29602 corrects an auxiliary satisfiability-case index; 30303–30304 has a recoverable comparison timeout; 30787–30788 further comparisons pass; 30790 reaches budget cap.

**Inferred — crux.** Yes: complete order search.

**Inferred — commitment.** An auxiliary expected-unsatisfiable index was wrong.

**Inferred — recovery.** Verified corrected edge checks; final completion censored.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### kimi-k3 · replicate 3 · excluded: budget_limit

Raw trial: `atomic-range-history__UdWdk7m`. Trajectory SHA-256: `c3be918e52f7ec64619afc47dd5e59a577889b9beb5a09bfa4b8b220f419fb12`.

**Verified — events.** 23888–23889 implements solver and passes smoke; 25224–27054 comparison batches report zero bad cases; 28585–28997 edges and larger permutation comparisons pass; 33938–33939 performance search completes; 33941 reaches budget cap.

**Inferred — crux.** Yes: real-time-constrained replay search.

**Inferred — commitment.** No candidate error observed.

**Inferred — recovery.** No recovery needed; final completion censored.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### kimi-k3 · replicate 4 · excluded: budget_limit

Raw trial: `atomic-range-history__gCrj2sd`. Trajectory SHA-256: `eda1307038dc17f4a563b860f4df2ba73a8e0b4f500f7bf18cf510d5e60699a2`.

**Verified — events.** 14568–14569 implements solver and passes smoke; 16531–18179 random and larger comparisons pass; 21114–21115 stress hunt has recoverable timeout; 26487–30251 optimizes feasibility and repeats checks successfully; 31643–31644 completes 300-case CLI batch; 31646 reaches budget cap.

**Inferred — crux.** Yes: exhaustive replay with feasibility pruning.

**Inferred — commitment.** No failed candidate observed in reviewed windows.

**Inferred — recovery.** Final completion censored after successful comparison and CLI checks.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

### kimi-k3 · replicate 5 · excluded: budget_limit

Raw trial: `atomic-range-history__AmEa4wh`. Trajectory SHA-256: `90a10e3f572e93c6385615a11eec2defebfc82fe1782328a1bde808a1738e28e`.

**Verified — events.** 9723–9724 implements solver and passes smoke; 11960–12272 repairs random generator then observes 49 bad cases in 1100; 15814–15815 rewrites solver, zero bad cases; 16441–16442 passes 10000 comparisons; 18988–19970 fixes satisfiability labels in stress tests; 23695–23696 one scan-isolation expectation disagrees; 23698 reaches budget cap.

**Inferred — crux.** Yes: search and semantic replay.

**Inferred — commitment.** Initial candidate disagreed with differential checks; a later edge expectation remains unresolved.

**Inferred — recovery.** Verified recovery on differential comparisons; unknown for the final scan expectation.

**Mechanism judgment.** Verified: final result is censored (ProxyBudgetExceeded); no final semantic failure is established. Qualitative observations do not enter the pass-rate denominator.

