"""Every non-item action must avoid simulated console input."""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import vein_helper as h
for command in h.DIRECT_COMMANDS:
    app=SimpleNamespace(busy=False,armed=SimpleNamespace(get=lambda:True),
        connected=Mock(),bridge=None,note=Mock(),root=Mock(),native_receipt=Mock())
    with patch.object(h,'game_windows',return_value=[123]),patch.object(h,'Bridge') as factory,patch.object(h,'send_to_console') as console,patch.object(h,'sound') as tone:
        h.App.execute(app,command)
        assert app.busy
        factory.return_value.submit.assert_called_once_with(command)
        console.assert_not_called()
        factory.return_value.poll.return_value=True
        done=Mock()
        h.App.native_receipt(app,done)
        assert not app.busy
        tone.assert_called_once_with('done')
        assert app.root.after.call_args.args==(150,done)
        console.assert_not_called()
print(f'All {len(h.DIRECT_COMMANDS)} direct actions avoid console; completion and sound: PASS')
