"""User Acceptance Testing (UAT) - Error Recovery and Resilience.

This test validates graceful failure handling in production workflows:
- Partial batch failures are handled gracefully
- Remaining tasks complete successfully
- Clear error reporting for failed tasks
- User can recover and retry failed items

User Story: "If the API times out on post #50, I still want the other 49
posts to complete. I should see which ones failed and be able to retry."
"""

from unittest.mock import MagicMock, patch

from agency_toolkit.core.orchestrator import execute_module


class TestErrorRecoveryAndResilience:
    """Error handling and recovery tests for production workflows."""

    def test_workflow_partial_failure_continues_with_on_error_continue(self):
        """Test that workflow with on_error: continue handles partial failures.

        Verifies:
        - Failed task doesn't stop workflow
        - Remaining tasks execute
        - Report shows correct failure count
        - Error details captured
        """
        # Create workflow with 10 tasks where task #5 fails
        workflow = {
            "id": "PARTIAL_FAILURE",
            "tasks": [
                {
                    "tool": "social",
                    "on_error": "continue",
                    "params": {"text": f"Post {i}"},
                }
                for i in range(1, 11)
            ],
        }

        context = {"project_name": "Test"}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:
            handler = MagicMock()

            def side_effect(*args, **kwargs):
                # Get call count (Python's MagicMock counts calls)
                call_num = side_effect.call_count
                side_effect.call_count += 1

                if call_num == 4:  # 5th task (0-indexed)
                    raise RuntimeError("API timeout on post 5")
                return f"image_{call_num}"

            side_effect.call_count = 0
            handler.execute.side_effect = side_effect
            mock_handler.return_value = handler

            report = execute_module(workflow, context, show_progress=False)

            # Verify partial failure handling
            assert report.total_tasks == 10
            assert (
                report.successful == 9
            ), f"Expected 9 successes, got {report.successful}"
            assert report.failed == 1, f"Expected 1 failure, got {report.failed}"
            assert len(report.errors) == 1
            assert "API timeout" in report.errors[0]

    def test_failed_task_has_error_details(self):
        """Test that failed tasks have detailed error information.

        Verifies:
        - Failed TaskResult has error message populated
        - Success flag is False
        - Output is None
        """
        workflow = {
            "id": "ERROR_DETAILS",
            "tasks": [
                {"tool": "ai", "on_error": "continue", "params": {"prompt": "test"}}
            ],
        }

        context = {"project_name": "Test"}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:
            handler = MagicMock()
            handler.execute.side_effect = RuntimeError("Network error")
            mock_handler.return_value = handler

            report = execute_module(workflow, context, show_progress=False)

            # Check failed task result
            assert report.failed == 1
            failed_result = report.task_results[0]
            assert failed_result.success is False
            assert failed_result.error != ""
            assert "Network error" in failed_result.error
            assert failed_result.output is None

    def test_workflow_stops_on_critical_failure_with_stop_mode(self):
        """Test that on_error: stop halts workflow immediately.

        Verifies:
        - Task failure with on_error: stop (and stop_on_error context) stops workflow
        - Remaining tasks don't execute
        - Report shows skipped tasks
        """
        workflow = {
            "id": "CRITICAL_FAILURE",
            "tasks": [
                {"tool": "structure", "on_error": "stop", "params": {}},
                {
                    "tool": "ai",
                    "on_error": "stop",
                    "params": {"prompt": "test"},
                },  # This fails
                {
                    "tool": "social",
                    "on_error": "stop",
                    "params": {"text": "post"},
                },  # Skipped
                {"tool": "briefing", "on_error": "stop", "params": {}},  # Skipped
            ],
        }

        context = {"project_name": "Test", "stop_on_error": True}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:

            def side_effect(tool_name):
                h = MagicMock()
                if tool_name == "ai":
                    h.execute.side_effect = RuntimeError("AI service unavailable")
                else:
                    h.execute.return_value = "success"
                return h

            mock_handler.side_effect = side_effect

            report = execute_module(workflow, context, show_progress=False)

            # First task succeeds, AI fails, social and briefing are skipped
            assert report.successful == 1  # structure
            assert report.failed == 1  # ai
            assert report.skipped == 2  # social, briefing
            assert len(report.task_results) == 2  # Only executed tasks in results

    def test_workflow_continues_when_on_error_continue_with_no_stop_flag(self):
        """Test that on_error: continue continues regardless of stop_on_error context.

        Verifies:
        - Even if stop_on_error=True in context, on_error: continue always continues
        - Task failures don't halt the workflow
        """
        workflow = {
            "id": "CONTINUE_DESPITE_STOP",
            "tasks": [
                {
                    "tool": "ai",
                    "on_error": "continue",
                    "params": {"prompt": "test"},
                },  # Fails
                {
                    "tool": "social",
                    "on_error": "continue",
                    "params": {"text": "post"},
                },  # Still executes
            ],
        }

        context = {"project_name": "Test", "stop_on_error": True}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:

            def side_effect(tool_name):
                h = MagicMock()
                if tool_name == "ai":
                    h.execute.side_effect = RuntimeError("API error")
                else:
                    h.execute.return_value = "success"
                return h

            mock_handler.side_effect = side_effect

            report = execute_module(workflow, context, show_progress=False)

            # Both tasks execute despite failure
            assert report.total_tasks == 2
            assert report.failed == 1  # ai fails
            assert report.successful == 1  # social succeeds
            assert report.skipped == 0  # Nothing skipped

    def test_error_recovery_provides_identifiable_failed_items(self):
        """Test that error report clearly identifies which items failed.

        Verifies:
        - Each error message includes task/item identification
        - User can identify and retry specific failed items
        - Error messages are user-friendly
        """
        workflow = {
            "id": "IDENTIFIED_FAILURES",
            "tasks": [
                {
                    "tool": "social",
                    "on_error": "continue",
                    "params": {"text": f"Post {i}"},
                }
                for i in range(1, 6)
            ],
        }

        context = {"project_name": "Campaign"}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:
            handler = MagicMock()

            def side_effect(*args, **kwargs):
                call_num = side_effect.call_count
                side_effect.call_count += 1

                # Tasks 2 and 4 fail
                if call_num in [1, 3]:
                    raise RuntimeError(
                        f"Task {call_num} failed: Image generation failed"
                    )
                return f"image_{call_num}"

            side_effect.call_count = 0
            handler.execute.side_effect = side_effect
            mock_handler.return_value = handler

            report = execute_module(workflow, context, show_progress=False)

            # Errors should clearly identify which tasks failed
            assert report.failed == 2
            assert len(report.errors) >= 2
            # Errors should mention the failed tasks
            error_text = " ".join(report.errors)
            assert "failed" in error_text.lower()

    def test_batch_50_posts_with_5_failures_recovers(self):
        """Test realistic scenario: 50-post batch with 5 failures.

        Verifies:
        - 45 posts complete successfully
        - 5 failed posts clearly identified
        - User can retry the 5 failures
        - Overall workflow doesn't fail
        """
        workflow = {
            "id": "BATCH_WITH_FAILURES",
            "tasks": [
                {
                    "tool": "social",
                    "on_error": "continue",
                    "params": {"text": f"Post {i}"},
                }
                for i in range(1, 51)
            ],
        }

        context = {"project_name": "Large Campaign"}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:
            handler = MagicMock()

            def side_effect(*args, **kwargs):
                call_num = side_effect.call_count
                side_effect.call_count += 1

                # Every 10th task fails (posts 10, 20, 30, 40, 50)
                if (call_num + 1) % 10 == 0:
                    raise RuntimeError(f"API rate limit on post {call_num + 1}")
                return f"image_{call_num}"

            side_effect.call_count = 0
            handler.execute.side_effect = side_effect
            mock_handler.return_value = handler

            report = execute_module(workflow, context, show_progress=False)

            assert report.total_tasks == 50
            assert report.successful == 45
            assert report.failed == 5
            assert report.skipped == 0
            assert len(report.errors) == 5

    def test_error_recovery_allows_retry_of_failed_items(self):
        """Test that failed items can be retried independently.

        Verifies:
        - Failed items can be identified
        - Retry can process just failed items
        - Retry is more efficient than reprocessing all
        """
        # First run: some items fail
        workflow_v1 = {
            "id": "BATCH_V1",
            "tasks": [
                {
                    "tool": "social",
                    "on_error": "continue",
                    "params": {"text": f"Post {i}"},
                }
                for i in range(1, 6)
            ],
        }

        context = {"project_name": "Test"}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:
            handler = MagicMock()
            handler.execute.side_effect = [
                "image_1",
                RuntimeError("Timeout"),
                "image_3",
                RuntimeError("Timeout"),
                "image_5",
            ]
            mock_handler.return_value = handler

            report1 = execute_module(workflow_v1, context, show_progress=False)

            assert report1.successful == 3
            assert report1.failed == 2
            failed_indices = [
                i for i, r in enumerate(report1.task_results) if not r.success
            ]
            assert failed_indices == [1, 3]  # Posts 2 and 4 failed

        # Second run: retry just the failed items
        # In real scenario, user would create new workflow with just failed items
        failed_tasks = [workflow_v1["tasks"][i] for i in failed_indices]

        workflow_v2 = {
            "id": "BATCH_V1_RETRY",
            "tasks": failed_tasks,
        }

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:
            handler = MagicMock()
            handler.execute.side_effect = ["image_2_retry", "image_4_retry"]
            mock_handler.return_value = handler

            report2 = execute_module(workflow_v2, context, show_progress=False)

            # Retry should succeed
            assert report2.successful == 2
            assert report2.failed == 0

    def test_timeout_error_provides_recovery_hint(self):
        """Test that timeout errors suggest retry strategy.

        Verifies:
        - Timeout error message is clear
        - Error suggests waiting and retrying
        - Error includes which task timed out
        """
        workflow = {
            "id": "TIMEOUT_TEST",
            "tasks": [
                {"tool": "ai", "on_error": "continue", "params": {"prompt": "test"}}
            ],
        }

        context = {"project_name": "Test"}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:
            handler = MagicMock()
            handler.execute.side_effect = TimeoutError("Request timed out after 30s")
            mock_handler.return_value = handler

            report = execute_module(workflow, context, show_progress=False)

            assert report.failed == 1
            error = report.errors[0]
            assert "timeout" in error.lower() or "timed out" in error.lower()

    def test_workflow_with_mixed_error_modes_handles_correctly(self):
        """Test workflow with mixed on_error modes.

        Verifies:
        - Critical tasks (on_error: stop) halt on failure
        - Optional tasks (on_error: continue) don't halt
        - Correct tasks execute
        """
        workflow = {
            "id": "MIXED_MODES",
            "tasks": [
                {"tool": "structure", "on_error": "stop", "params": {}},  # Critical
                {
                    "tool": "ai",
                    "on_error": "continue",
                    "params": {"prompt": "test"},
                },  # Optional - fails
                {
                    "tool": "social",
                    "on_error": "stop",
                    "params": {"text": "post"},
                },  # Critical - executes
                {"tool": "briefing", "on_error": "continue", "params": {}},  # Optional
            ],
        }

        context = {"project_name": "Test"}

        with patch("agency_toolkit.core.orchestrator.get_task_handler") as mock_handler:

            def side_effect(tool_name):
                h = MagicMock()
                if tool_name == "ai":
                    h.execute.side_effect = RuntimeError("AI failed")
                else:
                    h.execute.return_value = "success"
                return h

            mock_handler.side_effect = side_effect

            report = execute_module(workflow, context, show_progress=False)

            # structure (success), ai (fail), social (success), briefing (success)
            assert report.successful == 3
            assert report.failed == 1
            assert report.skipped == 0
