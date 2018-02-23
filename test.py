from middleware import Client

client = Client()

result = client.register_pub("TEST", ownership_strength=4, history=5)
print(result)
result = client.register_sub("TEST")
print(result)
result = client.publish("TEST", 25)
print(result)
result = client.notify("TEST", 10)
print(result)
# response = middleware.register_sub("tcp://localhost:7777", "Test")

#print(response)