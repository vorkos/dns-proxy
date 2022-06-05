# dns-proxy
DNS to DNS-over-TLS proxy

[![Test and build](https://github.com/vorkos/dns-proxy/actions/workflows/test-build.yaml/badge.svg)](https://github.com/vorkos/dns-proxy/actions/workflows/test-build.yaml)

## Task

The task was to design and create a simple DNS to DNS-over-TLS proxy 
- being able to handle at least one DNS query
- work over TCP and talk to a DNS-over-TLS server that works over TCP (e.g: Cloudflare)

## Implementation

I've choose `socket` library as the most basic one for work with sockets and `ssl` for secure connections. There is a better option with `socketserver` library with more elegant solution, but I've choose a low level one to practice codding Python.

`ssl.Purpose.SERVER_AUTH` option gives good security defaults in my opinion.

I've used timeout value and buffer sizes from RFC's.

By default both TCP and UDP servers listen on the port 53. They work in parallel threads, could serve multiple requests, proxy requests to 1.1.1.1 DNS-over-TLS server. 
### Security concerns 
- It's an important part of network infrastructure, so the image should be deployed with all precautions, like using sha256 hash, etc.
- Being deployed as a central DNS proxy it could point of failure.
### How would I integrate this solution?
As a sidecar container for applications that don't have it's own DoT feature.

### Improvements ideas

- I see some code duplication, so It could be refactored.
- Better error handling on network calls.
- More careful work with threads, ensure all threads are closed after the response.
- Short living cache for responses.
- Better logging with only useful information.
- HA by using several upstream TLS resolvers.
- Unit tests
- Integration tests

## Deployment
[GitHub actions workflow](.github/workflows/test-build.yaml)

This repo has it's own GitHub actions pipeline with Python code static code analyzer and CD pipeline.
Every PR and release are built by the pipeline, docker images uploads to the [GitHub container registry](https://github.com/vorkos/dns-proxy/pkgs/container/dns-proxy) on release.
### Options
Environment variable | Description | Default
--- | --- | ---
`TLS_DNS_IP` | TLS DNS resolver hostname or IP | 1.1.1.1
`TLS_DNS_PORT` | Port of TLS DNS resolver | 853
`PROXY_PORT` | Local DNS proxy port for TCP and UDP | 53

### Run the proxy - 

`docker run -p 10054:53/tcp -p 10054:53/udp  -d ghcr.io/vorkos/dns-proxy:latest`
### Check the connection - 

`sudo tcpdump -vvv port 853` - listen for the traffic to the TLS resolver.

`kdig -d @localhost:10053  google.com A +tcp` - TCP query.

`kdig -d @localhost:10053  google.com A` - UDP query.