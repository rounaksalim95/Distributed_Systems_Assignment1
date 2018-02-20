import middleware

response = middleware.register_sub("tcp://localhost:7777", "Test", 1)

print(response)