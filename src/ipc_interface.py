"""
This is a home-brew protocol to connect any services with Adinkra.

(There may be an easier way for Python2 and Python3 programs to communicate with one another.
I may try to find a better solution but this works for now.)

You start by connecting to the host and port specified.
You can then start sending data in json format after connecting to the listener.
"""
# TODO: find better, easier way to interface this with django


# project dependencies
import log_handler

# system dependencies
import socket
import atexit
import sys
import datetime
import signal

# connection type constants
IPV4 = socket.AF_INET
IPV6 = socket.AF_INET6
#UNIX_SOCKET = socket.socket.AF_UNIX # usable on UNIX system but unusable on windows systems

TCP = socket.SOCK_STREAM
UDP = socket.SOCK_DGRAM

# default network connection parameters
LOCALHOST = "127.0.0.1"
DEFAULT_PORT_NUMBER = 65535
DEFAULT_MAX_QUEUED_CONNECTION = 5

# protocol specific signals
END_TRANSMISSION_SIGNAL = "ENDTRANSMISSION"  # clients: send this signal after you're done sending everything!
BEGIN_TRANSMISSION_SIGNAL = "BEGINTRANSMISSION"  # clients: send this signal to begin transmission
TRANSMISSION_SEPARATOR_SIGNAL = "NEWTRANSMISSION"  # clients: send this signal after sending a request to continue

REQUEST_COMPLETE_SIGNAL = "REQUESTCOMPLETE\r\n" # clients: this notifies that the request is complete


class IpcChannel:
	"""
	This class contains handlers for inter-process communication. It's primarily used to communicate with the
	Adinkra modules with the django backend for CSNAP, but should be robust enough for other interfaces.

	:member_variable host: the address the inter-process communication will go over; this is localhost in most cases.
	:member_variable port: the port the inter-process communication will go over.
	:member_variable num_connections: the maximum number of connections that can be queued
	:member_variable connection_type: what protocol to use for network packet delivery. This is typically UNIX sockets
									for Linux/BSD systems; IPV4 or IPV6 is typically used for other system or across
									systems.
	:member_variable protocol_type: what protocol to use for data delivery. This is typically TCP
	:member_variable log_file_descriptor: the log file to write network log entries to
	:member_variable ipc_socket: the socket that's responsible for communication

	:class_method request_response: Sends a response to the client after the request is complete.

	:member_method set_up_connection: Uses the initialized protocol parameters to initialize a connection for
										inter-process communication
	:member_method listen_for_requests: Goes into an infinite loop, listens and give requests until termination.
										This is a generator; thus, this should be treated as an iterator rather than
										a function.
	:member_method cleanup: Cleans up system resources used to set up the communication
	"""

	def __init__(self,
	                host=LOCALHOST,
	                port=DEFAULT_PORT_NUMBER,
	                num_connections=DEFAULT_MAX_QUEUED_CONNECTION,
	                connection_type=IPV4,
	                protocol_type=TCP,
	                log_file_directory=None
	             ):
		"""
		:optional_parameter host (str): The address to communicate over. LOCALHOST (default value) is recommended
											for typical usage.
		:optional_parameter port (int): The port number to communicate over. Default port is 65535.
		:optional_parameter num_connections (int): The maximum number of communication that can be queued.
													Default value is 5.
		:optional_parameter connection_type (socket module constant): The protocol to address network packets to.
																		Default value is IPV4
																		(abstracted out from socket.AF_INET)
		:optional_parameter protocol_type (socket module constant): The protocol to send network packets over.
																	Default value is TCP
																	(abstracted out from socket.SOCK_STREAM)
		:optional_parameter log_file_directory (str): The directory of the log file to write to. Default value
														signifies writing log entries to standard output.
		"""

		# variables are defined with default values if possible
		# if variables don't have default values, they are always None, 0, or ""
		self.host = host
		self.port = port
		self.num_connections = num_connections
		self.connection_type = connection_type
		self.protocol_type = protocol_type
		self.log_file_descriptor = sys.stdout
		self.ipc_socket = None

		if log_file_directory:
			try:
				self.log_file_descriptor = open(log_file_directory, "a")
			except Exception as error_msg: # can't open file; defaulting to standard out.
				log_handler.log_write_fderr(self.log_file_descriptor, "file open error", str(error_msg))
				self.log_file_descriptor = sys.stdout

		# cleanup function(s) goes here
		atexit.register(self.cleanup)
		signal.signal(signal.SIGTERM, self.cleanup)
		signal.signal(signal.SIGINT, self.cleanup)


	def set_up_connection(self):
		"""
		Initializes a socket to listen on.
		"""

		self.ipc_socket = socket.socket(self.connection_type, self.protocol_type)
		listening_location = (self.host, self.port)

		# establishing a listening server
		try:
			self.ipc_socket.bind(listening_location)
			self.ipc_socket.listen(self.num_connections)
			log_handler.log_write_fdout(self.log_file_descriptor, "listening on " + str(listening_location))
		except Exception as error_msg:
			log_handler.log_write_fderr(self.log_file_descriptor, "socket error", str(error_msg))


	def listen_for_requests(self):
		"""
		Keeps listening and give requests.
		This is a generator, so it must be treated as an iterator that gives the next available data.

		:return: (str) A data string containing adinkra request parameters and data in json-format.
		"""

		keep_receiving_connection = True # might be used in the future; always True for infinite while loop for now

		# server loop to keep listening for connection requests; continues until program is closed
		while keep_receiving_connection:
			received_data = "" # holds data for a single transmission

			carriage_return_engaged = False
			transmission_begin = False

			connection, client_address = self.ipc_socket.accept()
			# accept connection if one is present

			log_handler.log_write_fdout(self.log_file_descriptor, "connected to " + str(client_address))

			line_data = "" # holds a line of data delimited by \r\n

			# should keep going until client sends "ENDTRANSMISSION"
			while line_data != END_TRANSMISSION_SIGNAL:
				data_bit = connection.recv(1) # grab data one byte at a time

				if data_bit == "\r":
					carriage_return_engaged = True
				elif data_bit == "\n" and carriage_return_engaged: # \r\n delimiter detected
					if line_data == BEGIN_TRANSMISSION_SIGNAL:
						transmission_begin = True
					elif line_data == TRANSMISSION_SEPARATOR_SIGNAL:
						yield (connection, client_address, received_data) # give data for other functions to process

						received_data = ""
						transmission_begin = False
					elif transmission_begin:
						received_data += line_data

					line_data = ""
					carriage_return_engaged = False
				else: # allows either \r or \n in data, but not together
					carriage_return_engaged = False
					line_data += data_bit

			if len(received_data) > 0: # give whatever leftover data is present
				yield (connection, client_address, received_data)

			connection.shutdown(socket.SHUT_RDWR) # stops further reads and writes
			connection.close()
			log_handler.log_write_fdout(self.log_file_descriptor, "connection to " + str(client_address)
			                            + " is closed.")


	@staticmethod
	def request_response(connection, stl_directory):
		"""
		Send a response the connected client signifies that the adinkra request is complete

		:param connection: (socket object) A socket containing the connection to the client.
		:param stl_directory: (str) A string containing the directory to the resulting stl file.
		"""
		stl_directory_string = "stl:" + stl_directory + "\r\n"

		connection.send(REQUEST_COMPLETE_SIGNAL)
		connection.send(stl_directory_string)


	def cleanup(self):
		"""
		Cleanups up any resource (socket, files, etc.) the class has requested.
		"""

		print "cleaning up..."

		if self.ipc_socket:
			self.ipc_socket.close()

		if self.log_file_descriptor != sys.stdout:
			try:
				self.log_file_descriptor.close()
			except Exception as error_msg:
				print("[" + str(datetime.datetime.utcnow()) + "] {file close error:} " + str(error_msg))
		# don't close sys.stdout! Horrible bugs may occur
