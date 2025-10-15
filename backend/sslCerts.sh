# generate an rsa private key
openssl genrsa -out key.pem 4096
# generate a certificate signing request
openssl req -new -key key.pem -out cert.csr
# generate a certificate using the private key (answer questions)
openssl x509 -req -days 365 -in cert.csr -signkey key.pem -out cert.pem