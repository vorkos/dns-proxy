# dns-proxy
DNS to DNS-over-TLS proxy


### Check the connection - 
`sudo tcpdump -vvv port 853`
`kdig -d @localhost:10053  google.com A +tcp `