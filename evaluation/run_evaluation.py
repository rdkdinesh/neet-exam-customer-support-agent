import asyncio
import json

from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.evaluate import AsyncConfig, CacheConfig

from evaluation.metrics import create_metrics
from evaluation.test_cases import execute_all_questions


DATASET_FILE = (
    "evaluation/datasets/neet_test_cases.json"
)


def load_dataset():

    with open(
        DATASET_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


async def run_autogen_tests(dataset):

    questions = [
        test_data["input"]
        for test_data in dataset
    ]

    results = await execute_all_questions(
        questions
    )

    return results


def main():

    dataset = load_dataset()

    print()
    print("=" * 70)
    print(
        "NEET MULTI-AGENT CUSTOMER SUPPORT"
    )
    print(
        "DEEPEVAL EVALUATION"
    )
    print("=" * 70)

    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Run ALL AutoGen test cases inside ONE event loop.
    # --------------------------------------------------------

    results = asyncio.run(
        run_autogen_tests(dataset)
    )

    # --------------------------------------------------------
    # Build DeepEval test cases
    # --------------------------------------------------------

    test_cases = []

    for index, (
        test_data,
        result
    ) in enumerate(
        zip(dataset, results),
        start=1
    ):

        question = test_data["input"]

        expected_output = (
            test_data["expected_output"]
        )

        actual_output = result["answer"]

        print()
        print("=" * 70)
        print(
            f"TEST CASE {index}"
        )
        print("=" * 70)

        print(
            f"QUESTION:\n{question}"
        )

        print()

        print(
            f"FINAL ANSWER:\n{actual_output}"
        )

        test_case = LLMTestCase(
            input=question,
            actual_output=actual_output,
            expected_output=expected_output,
            retrieval_context=result.get("retrieval_context", [])
        )

        test_cases.append(
            test_case
        )

    # --------------------------------------------------------
    # DeepEval
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print(
        "RUNNING DEEPEVAL METRICS"
    )
    print("=" * 70)

    metrics = create_metrics()

    results = evaluate(
        test_cases=test_cases,
        metrics=metrics,
        async_config=AsyncConfig(
            run_async=False
        ),
        cache_config=CacheConfig(
            use_cache=False,
            write_cache=False
        )
    )

    print()
    print("=" * 80)
    print("NEET CUSTOMER SUPPORT EVALUATION COMPLETE")
    print("=" * 80)

    for test_index, test_result in enumerate(
        results.test_results,
        start=1
    ):

        print()
        print(f"TEST CASE #{test_index}")
        print("-" * 80)

        print(f"Question: {test_result.input}")

        for metric_data in test_result.metrics_data:

            score = (
                f"{metric_data.score:.4f}"
                if metric_data.score is not None
                else "N/A"
            )

            status = "PASS" if metric_data.success else "FAIL"

            print(
                f"{metric_data.name:35} "
                f"Score: {score:>8} "
                f"Status: {status}"
            )

    print()
    print("=" * 80)
    print("END OF EVALUATION")
    print("=" * 80)


if __name__ == "__main__":

    main()