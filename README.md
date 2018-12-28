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

`dui` will look for your last 1000 upvoted image posts (this is a Reddit API limitation) and download their images to `data/$subreddit`.

A cache is kept in `cache`, so that you can re-run `dui` periodically, without re-downloading any images you've recently retrieved.

