"""
TODO: file summary
"""


import datetime


def log_write_fdout(file_descriptor, message, delimiter="\r\n"):
	"""
	Writes message to the specified log file.

	:required_parameter file_descriptor (file descriptor): The file descriptor of the log file
	:required_parameter message (str): the message to write to the log file
	:optional_parameter delimiter (str): the newline delimiter to separate log entries. Default value is \r\n.
	"""

	output_string = "[" + str(datetime.datetime.utcnow()) + "] " + message + delimiter
	file_descriptor.write(output_string)


def log_write_fderr(file_descriptor, error_type, message, delimiter="\r\n"):
	"""
	Writes error message to the specified log file.

	:required_parameter file_descriptor (file descriptor): The file descriptor of the log file
	:required_parameter error_type:
	:required_parameter message (str): the message to write to the log file
	:optional_parameter delimiter (str): the newline delimiter to separate log entries. Default value is \r\n.
	"""

	error_string = "[" + str(datetime.datetime.utcnow()) + "] {" + error_type + "} " + message + delimiter
	file_descriptor.write(error_string)

