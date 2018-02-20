import middleware

# response = middleware.register_sub("tcp://localhost:7777", "Test", 1)
middleware.notify("tcp://localhost:7777", "my_address", "Test")

# print(response)