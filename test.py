import middleware

response = middleware.register_pub("my address", "tcp://localhost:7777", "Test")
# response = middleware.register_sub("tcp://localhost:7777", "Test")

print(response)