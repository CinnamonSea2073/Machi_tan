// common helpers
async function api(path, opts={}){
  const res = await fetch(path, Object.assign({credentials:'same-origin'}, opts))
  if(!res.ok) throw new Error(await res.text())
  return res.json()
}

// chat-style modal
function showModal(contentHtml){
  const backdrop=document.createElement('div');backdrop.className='modal-backdrop';document.body.appendChild(backdrop)
  const modal=document.createElement('div');modal.className='modal chat-modal'
  modal.innerHTML = `
    <div class="chat-header"><button id="chatClose" class="btn btn-small">✕</button></div>
    <div class="chat-body">${contentHtml}</div>
    <div class="chat-footer" style="text-align:center;margin-top:12px"><button id="chatDone" class="btn">報告かんりょう！</button></div>
  `
  document.body.appendChild(modal)
  const closeModal = ()=>{try{document.body.removeChild(modal)}catch{};try{document.body.removeChild(backdrop)}catch{}}
  document.getElementById('chatClose').addEventListener('click', closeModal)
  document.getElementById('chatDone').addEventListener('click', closeModal)
  backdrop.addEventListener('click', closeModal)
}

function showRetryModal(){
  const backdrop=document.createElement('div');backdrop.className='modal-backdrop';document.body.appendChild(backdrop)
  const modal=document.createElement('div');modal.className='modal'
  modal.innerHTML = `
    <div style="font-weight:700;margin-bottom:8px">録音が短すぎます</div>
    <div style="margin-bottom:12px">音声が小さいか無音の可能性があります。もう一度ゆっくり話してみてください。</div>
    <div style="text-align:center"><button id="retryRecord" class="btn" style="margin-right:8px">もう一度録る</button><button id="cancelRetry" class="btn btn-small">キャンセル</button></div>
  `
  document.body.appendChild(modal)
  const close = ()=>{try{document.body.removeChild(modal)}catch{};try{document.body.removeChild(backdrop)}catch{}}
  document.getElementById('cancelRetry').addEventListener('click', close)
  document.getElementById('retryRecord').addEventListener('click', ()=>{close(); document.getElementById('voiceBtn').click();})
}
