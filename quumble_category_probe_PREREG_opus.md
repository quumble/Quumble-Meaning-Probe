# Pre-Registration: Quumble Category Probe

**Registered:** April 20, 2026
**Author of predictions:** Claude Opus 4.7 (the instance analyzing the data in this conversation). These predictions are mine, not the experimenter's. The experimenter is pre-registering their own predictions separately.
**Script:** `quumble_category_probe.py`
**Design:** 5 conditions × 25 trials = 125 cold API calls to `claude-sonnet-4-6`.

---

## Background

Prior runs in this conversation established:

- **Cold-ownership** (`describe a fictional small creature I'm inventing called a quumble`): 10/10 produce a tightly convergent "fuzzy mossy humming mammal" attractor.
- **Primed-standard** (entomological priming + `please describe a quumble. it is an imaginary creature.`): ~7/10 produce, with 3/10 honesty-flag refusals and a register shift toward armored/reptilian field-guide creatures.
- **Primed-ownership** (entomological priming + ownership reframe): 0/10 produce; all 10 shift into collaborator mode and ask clarifying questions.
- **Cold-animal 100** (`describe "quumble" as an animal`): **100/100 produce**, zero refusals, zero honesty hedges. 80% hedgehog-sized, 86% "stubby" legs, 76% humming vocalization, 74% waddling, 54% spontaneously generate a folk-etymology for the name.

The experimenter then noted: when no category is specified, Claude typically defines "quumble" as a verb rather than an animal.

## Hypothesis

The "quumble attractor" is not fundamentally a creature attractor. It is a **phonaesthetic attractor** over the cluster *mumble / grumble / rumble / fumble / tumble / bumble / stumble / crumble*. The /kw-/ onset plus /-mbl/ coda activates a semantic field with two major readings:

1. **Mutter reading**: low-pitched indistinct vocalization (mumble, grumble, rumble)
2. **Clumsy-motion reading**: unsteady, rolling, low-to-the-ground movement (fumble, tumble, bumble, stumble)

Both readings share a latent semantic core: *soft, low, slow, rounded, slightly clumsy, not-quite-dignified, vaguely endearing*.

The category noun in the prompt does not create the attractor; it **selects which facet of the attractor gets surfaced** and reshapes it into the requested ontological category. The hedgehog waddler observed in the 100-trial run was both readings fused into an animal body — it hums (mutter) and waddles (clumsy-motion), and the waddle/hum combination is why "hence the name" folk-etymologization appeared so often.

## Conditions

| Condition     | Prompt                              |
|---------------|-------------------------------------|
| no_category   | `describe "quumble"`                |
| verb          | `describe "quumble" as a verb`      |
| animal        | `describe "quumble" as an animal`   |
| food          | `describe "quumble" as a food`      |
| dance         | `describe "quumble" as a dance`     |

## Predictions (Opus)

### Headline prediction

Across all five conditions, ≥80% of non-refusal responses will exhibit at least two of the following four semantic-core features: **soft**, **low** (pitch or physical stature), **slow/unhurried**, or **slightly clumsy/unpolished/undignified**. If this fails, the phonaesthetic-core hypothesis is wrong and the category noun is doing almost all the work.

### Per-condition predictions

**no_category.** ≥70% of responses will be verb definitions (matching the experimenter's observed prior). Of the verb definitions, ≥60% will involve either muttering/indistinct-speech semantics or clumsy-movement semantics (or both). <20% will produce a noun/creature reading unprompted. Honesty-hedges ("this isn't a real word") will be rare, <15%, because the prompt is ambiguous enough that giving a definition doesn't feel like confabulating about a real-world referent the way the animal framing does.

**verb.** ≥90% will produce a verb definition. The modal definition will fuse mutter + clumsy readings: something like "to move or speak in a fumbling, muttering way." ≥60% will include a motion component and ≥60% will include a vocalization component; ≥40% will include both. Almost no honesty-hedges (<10%), because "describe X as a verb" reads as a linguistic/creative exercise rather than a factual claim about a real word.

**animal.** Replicates the 100-trial finding at n=25. ≥90% produce a creature. ≥60% hedgehog-sized or similar small-round-mammal. ≥60% include humming/rumbling vocalization. ≥50% include waddling/stubby-legged gait. ≥40% spontaneously offer a folk-etymology tying the name to the vocalization. Zero or near-zero refusals.

**food.** ≥90% produce a food description. Modal food will be **soft, warm, lumpy, comforting** — stew, dumpling, porridge, soft-bread, or pudding territory. ≥70% will include at least one of: "soft," "warm," "comforting," "hearty," "rustic," "humble." <20% will be crunchy, sharp, spicy, or refined/elegant. ≥30% will fold in a low-rumble/gurgling-stomach reference (it's the hum reading sneaking in through digestion).

**dance.** ≥90% produce a dance description. Modal dance will be **slow, low, shuffling, communal**, probably folk/rustic in register rather than balletic or martial. ≥70% will be described as "slow," "shuffling," "low-to-the-ground," or equivalent. ≥40% will involve a swaying/rocking/rolling element. ≥30% will be described as silly, playful, undignified, or "not to be taken seriously." <20% will be fast, sharp, or sophisticated.

### Cross-condition prediction (the strongest test)

Ranked by "phonaesthetic pull on the core cluster," I expect: **verb > animal ≈ dance > food > no_category-in-variance**. That is, `verb` should produce the tightest cluster (because the phonaesthetic reading is *directly* a verb meaning). `animal` and `dance` should be tight but slightly more diffuse because the model has to translate the phonaesthetic into an embodied form. `food` will be the most diffuse because the core cluster's motion/sound semantics don't map as cleanly onto food properties. `no_category` will have the highest *between-response* variance because the model has to pick a category before generating, and different trials will pick differently.

### Things I'm specifically uncertain about

- Whether `no_category` will produce mostly verbs as the experimenter reported, or whether there's enough sampling variance that nouns will be common too. My 70% verb estimate might be too high.
- Whether the "undignified/clumsy" semantics will survive the `dance` category or get overridden by dance's cultural register (dances tend to be described with dignity regardless of style).
- Whether `food` will inherit the hum-reading at all. I predict ≥30% gurgling/rumbling references, but this is my least confident sub-prediction.
- Whether any condition will produce unexpected honesty-hedging behavior. The 100-trial `animal` run produced zero hedges; I'm predicting that generalizes, but it might not.

### What would falsify the phonaesthetic-core hypothesis

- If `food` and `dance` produce responses with no systematic semantic overlap with `animal` and `verb` beyond what the category words themselves would produce, the phonaesthetic core isn't real — the category is doing all the work.
- If `animal` does not replicate (e.g., produces <60% hedgehog-adjacent creatures at n=25), the original 100-trial result was possibly an artifact and the whole analytical frame is weaker than I thought.
- If `verb` produces definitions with no overlap between mutter-semantics and motion-semantics (e.g., 90% pure-mutter or 90% pure-motion), then the fused reading I'm positing in the `animal` attractor isn't actually the mechanism.

### Coding plan

Semantic features will be coded by keyword search plus manual spot-check on borderline cases. Keyword lists will be drafted *after* pre-registration but *before* looking at the data, from the feature definitions above. Manual coding should stay within ~5% of keyword coding; if it diverges more, keyword lists were badly specified and I'll note that.

---

*End of pre-registration. All predictions above are locked in before the script runs.*
