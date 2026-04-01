import pytest
from unittest.mock import patch, MagicMock
from core.monitor import IdleMonitor


@pytest.fixture
def mock_windll():
    mock_user32 = MagicMock()
    mock_kernel32 = MagicMock()
    mock_user32.GetLastInputInfo.return_value = True
    mock_kernel32.GetTickCount.return_value = 1000
    mock_user32.GetLastInputInfo = MagicMock(return_value=True)

    mock_windll = MagicMock()
    mock_windll.user32 = mock_user32
    mock_windll.kernel32 = mock_kernel32

    with patch("ctypes.windll", mock_windll):
        yield mock_windll


def test_get_idle_seconds(mock_windll):
    monitor = IdleMonitor()
    # Test: if dwTime = 0, tick = 1000, idle = 1s
    mock_windll.user32.GetLastInputInfo.side_effect = lambda x: setattr(
        x.contents, "dwTime", 0
    )
    assert monitor.get_idle_seconds() == 1.0


def test_set_keep_awake(mock_windll):
    monitor = IdleMonitor()
    monitor.set_keep_awake(True)
    mock_windll.kernel32.SetThreadExecutionState.assert_called()


def test_execute_action():
    monitor = IdleMonitor()
    with patch("os.system") as mock_system, \
         patch("core.logger.logger") as mock_logger:
        monitor.execute_action("shutdown")
        mock_system.assert_called_with("shutdown /s /t 0 /f")
        mock_logger.info.assert_called()
