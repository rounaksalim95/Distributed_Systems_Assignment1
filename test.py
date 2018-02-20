import middleware

response = middleware.register_pub("my_address", "tcp://localhost:7777", "Test", ownership_strength=10)
# response = middleware.register_sub("tcp://localhost:7777", "Test")

print(response)