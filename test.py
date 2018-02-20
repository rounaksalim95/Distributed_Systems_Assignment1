from middleware import Client

client = Client()

result = client.register_pub("TEST")
print(result)
# response = middleware.register_sub("tcp://localhost:7777", "Test")

#print(response)