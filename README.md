# dui - download upvoted images
## Usage

1. Build Docker container using `docker build . -t dui`
2. Copy `dui_example.ini` to `dui.ini` and set values for `reddit_{username,password,client_id,client_secret}`
3. Run with

	```bash
	docker run \
		-v $PWD/config:/config:ro \
		-v $PWD/data:/data \
		-v $PWD/cache:/cache \
		dui
	```

`dui` will look for your last 1000 upvoted image posts and download their originals to `data`, using

