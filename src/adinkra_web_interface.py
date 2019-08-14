"""
TODO: file summary
"""


# project dependencies
import ipc_interface
import adinkra_converter

# system dependencies
import argparse


def ipc_handler():
	"""
	TODO: documentation
	"""

	# setting up ipc channel
	ipc = ipc_interface.IpcChannel()
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
		# ipc_interface.IpcChannel.request_response(client, stl_directory)


def web_interface():
	ipc_handler()

if __name__ == "__main__":
	web_interface()