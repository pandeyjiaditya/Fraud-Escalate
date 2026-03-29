from layer0_privacy.normalization import process_privacy_layer

input_data = {
    "type": "text",
    "content": "my card number is 8102 5214 3697",
    "metadata": {}
}

result = process_privacy_layer(input_data)

print(result)