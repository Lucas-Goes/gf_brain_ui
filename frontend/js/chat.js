(function () {
    if (!document.getElementById('chat-session')) return;

    var placeholders = [
        "Qual fechamento atual?",
        "Qual regra de cadastro de clientes PF?",
        "Como funciona a migracao de clientes no GF?"
    ];
    var input = document.getElementById('main-input');
    var submitBtn = document.getElementById('submit-btn');
    var initialState = document.getElementById('initial-state');
    var chatSession = document.getElementById('chat-session');
    var bottomBar = document.getElementById('bottom-bar');
    var inputContainer = document.getElementById('input-container');

    function typeWriter(element, text, speed, callback) {
        var i = 0;
        element.innerHTML = '';
        element.classList.add('typing-cursor');

        function type() {
            if (i < text.length) {
                element.innerHTML += text.charAt(i);
                i++;
                var variance = Math.random() * 10;
                setTimeout(type, (speed || 20) + variance);
            } else {
                element.classList.remove('typing-cursor');
                if (callback) callback();
            }
        }
        type();
    }

    var placeholderRunning = true;

    function typePlaceholder(text, speed) {
        return new Promise(function (resolve) {
            var i = 0;
            input.placeholder = '_';

            function type() {
                if (!placeholderRunning) return resolve();
                if (i < text.length) {
                    input.placeholder = text.substring(0, i + 1) + '_';
                    i++;
                    setTimeout(type, (speed || 50) + Math.random() * 20);
                } else {
                    input.placeholder = text + '_';
                    setTimeout(function () {
                        input.placeholder = text;
                        setTimeout(resolve, 1500);
                    }, 500);
                }
            }
            type();
        });
    }

    async function rotatePlaceholderTypewriter() {
        while (placeholderRunning) {
            for (var i = 0; i < placeholders.length; i++) {
                if (!placeholderRunning) break;
                await typePlaceholder(placeholders[i]);
                if (!placeholderRunning) break;
                input.placeholder = '';
                await new Promise(function (r) { setTimeout(r, 300); });
            }
        }
    }

    function appendUserMessage(text) {
        var msgDiv = document.createElement('div');
        msgDiv.className = "flex flex-col items-end gap-2 max-w-[80%] ml-auto";
        msgDiv.innerHTML =
            '<div class="px-4 py-3 border-r-2 border-primary-container/40 text-on-surface font-body-md bg-transparent">' +
            text +
            '</div>' +
            '<span class="font-label-caps text-[10px] text-on-surface-variant">USER_ID_0X441 // ' +
            new Date().toLocaleTimeString() + '</span>';
        chatSession.appendChild(msgDiv);
        chatSession.scrollTop = chatSession.scrollHeight;
    }

    function appendAIResponse(text, fontes, escopo) {
        var msgDiv = document.createElement('div');
        msgDiv.className = "flex flex-col items-start gap-2 max-w-[85%]";
        var id = 'ai-resp-' + Date.now();
        var fontesHtml = '';
        if (fontes && fontes.length > 0) {
            fontesHtml = '<div class="flex flex-wrap gap-2 pt-2">' +
                fontes.map(function (f) {
                    return '<span class="font-label-caps text-[9px] text-on-surface-variant border border-on-surface-variant/20 px-2 py-0.5">' + f + '</span>';
                }).join('') +
                '</div>';
        }
        var escopoLabel = scopeLabelMap[escopo] || escopo;
        msgDiv.innerHTML =
            '<div class="relative pl-6">' +
            '<div class="absolute left-0 top-0 bottom-0 w-[3px] bg-[#ffb696]"></div>' +
            '<div class="p-6 bg-[#1c1b1b] border border-[#ffb696]/30 space-y-4">' +
            '<div class="flex items-center gap-2 text-[#ffb696] font-label-caps text-[12px]">' +
            '<span class="material-symbols-outlined text-[14px]" data-icon="security">security</span>' +
            'Escopo: ' + escopoLabel + '</div>' +
            '<div class="text-on-surface font-body-md leading-relaxed overflow-hidden response-content" id="' + id + '"></div>' +
            fontesHtml +
            '</div>' +
            '</div>' +
            '<span class="font-label-caps text-[10px] text-on-surface-variant ml-6 flex items-center gap-3">GF_BRAIN_V3 // ' +
            new Date().toLocaleTimeString() +
            '<button class="copy-btn hover:text-primary transition-colors" onclick="copyMsg(this)" title="Copiar resposta">' +
            '<span class="material-symbols-outlined text-[14px]" data-icon="content_copy">content_copy</span>' +
            '</button></span>';
        chatSession.appendChild(msgDiv);
        chatSession.scrollTop = chatSession.scrollHeight;

        var target = document.getElementById(id);
        text = text.replace(/\*\*/g, '');
        typeWriter(target, text, 20, function () {
            var html = target.innerHTML;
            html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, function (m, lang, code) {
                code = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                return '<div class="code-block-wrapper">' +
                    '<button class="copy-code-btn" onclick="copyCode(this)">' +
                    '<span class="material-symbols-outlined text-[14px]" data-icon="content_copy">content_copy</span>' +
                    ' Copiar</button>' +
                    '<pre class="code-snippet"><code>' + code + '</code></pre></div>';
            });
            target.innerHTML = html;
        });
    }

    function handleMessageSubmission() {
        var primaryVal = input.value.trim();
        var secondaryVal = document.getElementById('secondary-input').value.trim();
        var val = primaryVal || secondaryVal;

        if (val === '') return;

        if (!initialState.classList.contains('hidden')) {
            initialState.classList.add('hidden');
            chatSession.classList.remove('hidden');
            bottomBar.classList.remove('hidden');
            bottomBar.style.transform = 'translateY(100%)';
            requestAnimationFrame(function () {
                requestAnimationFrame(function () {
                    bottomBar.style.transform = 'translateY(0)';
                });
            });
        }

        submitBtn.disabled = true;
        document.getElementById('secondary-submit').disabled = true;
        appendUserMessage(val);
        input.value = '';
        document.getElementById('secondary-input').value = '';
        input.style.height = 'auto';
        appendAIResponse("Pensando...", null, escopoAtivo);

        var API_URL = 'http://127.0.0.1:8000/chat';

        var controller = new AbortController();
        var timeoutId = setTimeout(function () { controller.abort(); }, 60000);

        fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pergunta: val, escopo: escopoAtivo }),
            signal: controller.signal
        })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                clearTimeout(timeoutId);
                chatSession.removeChild(chatSession.lastElementChild);
                appendAIResponse(data.resposta, data.fontes, escopoAtivo);
            })
            .catch(function (err) {
                clearTimeout(timeoutId);
                chatSession.removeChild(chatSession.lastElementChild);
                console.error("Fetch error:", err);
                appendAIResponse("Erro ao conectar com a API. (" + err.message + ")");
            })
            .finally(function () {
                setTimeout(function () {
                    submitBtn.disabled = false;
                    document.getElementById('secondary-submit').disabled = false;
                }, 4500);
            });
    }

    submitBtn.addEventListener('click', handleMessageSubmission);
    document.getElementById('secondary-submit').addEventListener('click', handleMessageSubmission);

    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleMessageSubmission();
        }
    });

    document.getElementById('secondary-input').addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleMessageSubmission();
        }
    });

    var scopeBtns = document.querySelectorAll('.scope-btn');
    var scopeMap = ["codigo", "arquitetura", "documentacao", "automacao"];
    var scopeLabelMap = {
        "codigo": "Criar Código",
        "arquitetura": "Analisar Arquitetura",
        "documentacao": "Documentação",
        "automacao": "Automações",
    };
    var escopoAtivo = "codigo";

    function selectScope(btn) {
        scopeBtns.forEach(function (b) {
            b.style.borderColor = '';
            b.style.boxShadow = '';
        });
        btn.style.borderColor = '#ff6600';
        btn.style.boxShadow = '0 0 12px rgba(255,102,0,.25)';
        var idx = Array.prototype.indexOf.call(scopeBtns, btn);
        if (idx >= 0 && idx < scopeMap.length) {
            escopoAtivo = scopeMap[idx];
        }
    }

    selectScope(scopeBtns[0]);

    scopeBtns.forEach(function (btn) {
        btn.addEventListener('click', function () { selectScope(btn); });
    });

    document.addEventListener('mousemove', function (e) {
        var fragments = document.querySelectorAll('.code-fragment');
        var mouseX = e.clientX;
        var mouseY = e.clientY;
        fragments.forEach(function (frag, index) {
            var speed = (index + 1) * 0.03;
            var x = (window.innerWidth / 2 - mouseX) * speed * 0.05;
            var y = (window.innerHeight / 2 - mouseY) * speed * 0.05;
            frag.style.transform = 'translate(' + x + 'px, ' + y + 'px)';
        });
    });

    input.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });

    rotatePlaceholderTypewriter();

    window.copyCode = function (btn) {
        var pre = btn.parentElement.querySelector('.code-snippet code');
        if (!pre) return;
        var text = pre.textContent;
        navigator.clipboard.writeText(text).then(function () {
            var icon = btn.querySelector('.material-symbols-outlined');
            icon.textContent = 'check';
            var orig = btn.innerHTML;
            btn.innerHTML = '<span class="material-symbols-outlined text-[14px]" data-icon="check">check</span> Copiado!';
            setTimeout(function () { btn.innerHTML = orig; }, 2000);
        });
    };

    window.copyMsg = function (btn) {
        var container = btn.closest('.items-start');
        var textEl = container.querySelector('.text-on-surface');
        if (!textEl) return;
        var text = textEl.innerText;
        navigator.clipboard.writeText(text).then(function () {
            var icon = btn.querySelector('.material-symbols-outlined');
            icon.textContent = 'check';
            setTimeout(function () { icon.textContent = 'content_copy'; }, 2000);
        });
    };
})();
