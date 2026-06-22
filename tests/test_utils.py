import provworkflow.utils as utils


def test_now_as_xsd_datetime_stamp_uses_portable_isoformat(monkeypatch):
    class FakeDateTime:
        @classmethod
        def now(cls):
            return cls()

        def astimezone(self):
            return self

        def isoformat(self, timespec):
            assert timespec == "seconds"
            return "2026-06-19T15:31:14+08:00"

        def strftime(self, _format):
            raise AssertionError("strftime should not be used for timezone formatting")

    monkeypatch.setattr(utils, "datetime", FakeDateTime)

    assert utils.now_as_xsd_datetime_stamp() == "2026-06-19T15:31:14+08:00"
