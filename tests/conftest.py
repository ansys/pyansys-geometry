""""General testing fixtures."""
import logging as deflogging  # Default logging

import pytest


@pytest.fixture
def fake_record():
    def inner_fake_record(
        logger,
        msg="This is a message",
        instance_name="172.1.1.1:52000",
        handler_index=0,
        name_logger=None,
        level=deflogging.DEBUG,
        filename="fn",
        lno=0,
        args=(),
        exc_info=None,
        extra={},
    ):
        """
        Function to fake log records using the format from the logger handler.

        Parameters
        ----------
        logger : logging.Logger
            A logger object with at least a handler.
        msg : str, optional
            Message to include in the log record. By default 'This is a message'.
        instance_name : str, optional
            Name of the instance. By default '172.1.1.1:52000'.
        handler_index : int, optional
            Index of the selected handler in case you want to test a handler different than
            the first one. By default 0.
        level : int, optional
            Logging level, by default deflogging.DEBUG.
        filename : str, optional
            Name of the file name. [FAKE]. By default 'fn'.
        lno : int, optional
            Line where the fake log is recorded [FAKE]. By default 0.
        args : tuple, optional
            Other arguments. By default ().
        exc_info : [type], optional
            Exception information. By default `None`.
        extra : dict, optional
            Extra arguments, one of them should be 'instance_name'. By default `{}`.

        Returns
        -------
        str
            The formatted message according to the handler.
        """
        sinfo = None
        if not name_logger:
            name_logger = logger.name

        if "instance_name" not in extra.keys():
            extra["instance_name"] = instance_name

        record = logger.makeRecord(
            name_logger,
            level,
            filename,
            lno,
            msg,
            args=args,
            exc_info=exc_info,
            extra=extra,
            sinfo=sinfo,
        )
        handler = logger.handlers[handler_index]
        return handler.format(record)

    return inner_fake_record
