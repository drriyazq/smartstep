/// Baseline assessment. A YES answer marks the linked tasks as `bypassed`,
/// letting the child skip foundational tasks they've already mastered.
///
/// Revising these is a one-file edit.
class BaselineQuestion {
  const BaselineQuestion({required this.prompt, required this.bypassSlugs});
  final String prompt;
  final List<String> bypassSlugs;
}

const baselineQuestions = <BaselineQuestion>[
  BaselineQuestion(
    prompt: "Can your child read numeric price tags on their own?",
    bypassSlugs: ["read-price-tag"],
  ),
  BaselineQuestion(
    prompt: "Does your child already count coins and notes correctly?",
    bypassSlugs: ["count-change"],
  ),
  BaselineQuestion(
    prompt: "Has your child safely boiled water unaided before?",
    bypassSlugs: ["boil-water", "use-stove-knob"],
  ),
  BaselineQuestion(
    prompt: "Can your child crack an egg without shell fragments?",
    bypassSlugs: ["crack-egg"],
  ),
  BaselineQuestion(
    prompt: "Does your child already pack their own lunchbox?",
    bypassSlugs: ["pack-lunchbox"],
  ),
];
