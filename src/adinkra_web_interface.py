"""
This file contains the necessary parts for setting up a listening server for Adinkra requests.
This script is stand alone and can be invoked with command line arguments.
To understand those arguments, simply invoke `python adinkra_web_interface.py -h`

If you experience any errors, feel free to contact me at
                                                    email: jiruan@umich.edu
                                                    phone: +1-773-280-1417
"""


# project dependencies
import ipc_interface
import adinkra_converter

# system dependencies
import argparse


def web_handler(host, port, num_connection, log_file):
	"""
	Handles all the necessary parts to listen for and process Adinkra requests.

	:required_parameter host: A host to connect the Adinkra listener to.
	:required_parameter port: A port for the Adinkra listener to listen on.
	:reqiured_parameter num_connection: The maximum number of connections to queue.
	:required_parameter log_file: A directory for a log file to write to.
	"""

	# setting up ipc channel
	ipc = ipc_interface.IpcChannel(host=host,
	                               port=port,
	                               num_connections=num_connection,
	                               log_file_directory=log_file)
	ipc.set_up_connection()

	request_iterator = ipc.listen_for_requests()

	# main request loop
	for client, _, data in request_iterator:
		# parsing data from requests
		json_data = adinkra_converter.text_to_json(data)
		adinkra_parameters = adinkra_converter.compile_adinkra_parameters(json_data)

		# break out parameters from the tuple
		image_matrix = adinkra_parameters[0]
		stl_directory = adinkra_parameters[1]
		include_base = adinkra_parameters[2]
		smooth = adinkra_parameters[3]
		negative = adinkra_parameters[4]
		border = adinkra_parameters[5]
		size = adinkra_parameters[6]
		scale = adinkra_parameters[7]

		# convert adinkra design to stl
		adinkra_converter.convert_adinkra(image_matrix, stl_directory, include_base, smooth, negative, border, size,
		                                  scale)

		# send signal signifying that the adinkra is done
		#ipc_interface.IpcChannel.request_response(client, stl_directory)


def web_interface():
	"""
	An interface to set up a listener for adinkra requests.

	Usage: python2 ./adinkra_web_interface.py [-c/--connections number] [-l/--log-file directory] address port

	Example: python2 ./adinkra_web_interface.py --connections=5 --log-file=/var/log/test.log localhost 8800
	"""

	# command line arguments parsing
	parser = argparse.ArgumentParser(description="Set up a ipc server to process Adinkra requests.")

	parser.add_argument("-c", "--connections", metavar="number", type=int, nargs=1, default=5,
	                    help="the maximum number of connections that can be queued.")
	parser.add_argument("-l", "--log-file", metavar="directory", type=str, nargs=1, default=None,
	                    help="the log file to write log entries to.")

	parser.add_argument("address", type=str, help="the address to listen for requests on.")
	parser.add_argument("port", type=int, help="the port to listen on.")

	arguments = parser.parse_args()
	arg_dictionary = vars(arguments)

	# extract arguments
	address = arg_dictionary["address"]
	port = arg_dictionary["port"]

	if isinstance(arg_dictionary["connections"], list):
		num_connections = arg_dictionary["connections"][0]
	else:
		num_connections = 5

	if isinstance(arg_dictionary["log_file"], list):
		log_dir = arg_dictionary["log_file"][0]
	else:
		log_dir = None

	# pass arguments to handler
	web_handler(address, port, num_connections, log_dir)


if __name__ == "__main__":
	web_interface()
