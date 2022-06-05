# dns-proxy
DNS to DNS-over-TLS proxy

[![Test and build](https://github.com/vorkos/dns-proxy/actions/workflows/test-build.yaml/badge.svg)](https://github.com/vorkos/dns-proxy/actions/workflows/test-build.yaml)

### Check the connection - 
`sudo tcpdump -vvv port 853`
`kdig -d @localhost:10053  google.com A +tcp `