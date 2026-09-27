from deepeval.metrics import (
    AnswerRelevancyMetric,
    GEval,
    FaithfulnessMetric,
    ContextualRelevancyMetric
)

from deepeval.test_case import SingleTurnParams


def create_metrics():

    # ---------------------------------------------------------
    # 1. Answer Relevancy
    # ---------------------------------------------------------

    answer_relevancy = AnswerRelevancyMetric(
        threshold=0.70,
        model="gpt-4.1-mini",
        include_reason=True
    )

    # ---------------------------------------------------------
    # 2. NEET Answer Correctness
    # ---------------------------------------------------------

    correctness = GEval(
        name="NEET Answer Correctness",

        criteria="""
        Evaluate whether the actual answer correctly answers
        the user's NEET-related question.

        Consider:

        1. Factual correctness.
        2. Completeness.
        3. Directness.
        4. Important information that may be missing.
        5. Contradictions with the expected answer.
        6. Unsupported claims.

        For questions involving current NEET rules, eligibility,
        application requirements, counselling, dates or
        notifications, the answer should preferably rely on
        current official NTA or Government sources.

        Do not penalize harmless differences in wording.
        """,

        evaluation_params=[
            SingleTurnParams.INPUT,
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT
        ],

        threshold=0.70,
        model="gpt-4.1-mini"
    )

    # ---------------------------------------------------------
    # 3. Faithfulness
    # ---------------------------------------------------------

    faithfulness = FaithfulnessMetric(
        threshold=0.70,
        model="gpt-4.1-mini",
        include_reason=True
    )

    # ---------------------------------------------------------
    # 4. Contextual Relevancy
    # ---------------------------------------------------------

    contextual_relevancy = ContextualRelevancyMetric(
        threshold=0.70,
        model="gpt-4.1-mini",
        include_reason=True
    )

    return [
        answer_relevancy,
        correctness,
        faithfulness,
        contextual_relevancy
    ]