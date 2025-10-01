from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/")
async def index():
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset='utf-8' />
        <title>Machi_tan - Comments</title>
        <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
        <style>
          body { font-family: Arial, sans-serif; max-width: 800px; margin: 2rem auto; }
          .comment { border-bottom: 1px solid #ddd; padding: .5rem 0; }
          .meta { color: #666; font-size: .9rem; }
        </style>
      </head>
      <body>
        <div id="app">
          <h1>Comments</h1>

          <form @submit.prevent="submit">
            <div>
              <label>Author</label><br>
              <input v-model="author" required />
            </div>
            <div>
              <label>Comment</label><br>
              <textarea v-model="text" required></textarea>
            </div>
            <div>
              <button type="submit">Post</button>
            </div>
          </form>

          <h2>Recent</h2>
          <div v-if="loading">Loading...</div>
          <div v-else>
            <div v-if="comments.length === 0">No comments yet</div>
            <div v-for="c in comments" :key="c.id" class="comment">
              <div><strong>{{ c.author }}</strong></div>
              <div class="meta">{{ c.created_at }}</div>
              <div>{{ c.text }}</div>
            </div>
          </div>
        </div>

        <script>
        const { createApp } = Vue

        createApp({
          data() {
            return { author: '', text: '', comments: [], loading: true }
          },
          methods: {
            async load() {
              this.loading = true
              try {
                const res = await fetch('/api/comments')
                this.comments = await res.json()
              } finally {
                this.loading = false
              }
            },
            async submit() {
              if (!this.author || !this.text) return
              const payload = { author: this.author, text: this.text }
              const res = await fetch('/api/comments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
              })
              if (res.ok) {
                this.author = ''
                this.text = ''
                await this.load()
              } else {
                alert('Failed to post')
              }
            }
          },
          mounted() {
            this.load()
          }
        }).mount('#app')
        </script>
      </body>
    </html>
    """
    return Response(content=html, media_type="text/html")
