(function () {
    if (!document.getElementById('intro')) return;

    var introCanvas = document.getElementById('intro-particles');
    var introCtx = introCanvas.getContext('2d');
    var introParticles = [];

    function initIntroParticles() {
        introCanvas.width = window.innerWidth;
        introCanvas.height = window.innerHeight;
        introParticles = [];
        var count = (introCanvas.height * introCanvas.width) / 15000;
        for (var i = 0; i < count; i++) {
            introParticles.push({
                x: Math.random() * introCanvas.width,
                y: Math.random() * introCanvas.height,
                dx: (Math.random() - 0.5) * 0.5,
                dy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1
            });
        }
    }

    function animateIntroParticles() {
        introCtx.clearRect(0, 0, introCanvas.width, introCanvas.height);
        introParticles.forEach(function (p) {
            p.x += p.dx;
            p.y += p.dy;
            if (p.x < 0 || p.x > introCanvas.width) p.dx *= -1;
            if (p.y < 0 || p.y > introCanvas.height) p.dy *= -1;
            introCtx.beginPath();
            introCtx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            introCtx.fillStyle = '#FF6B00';
            introCtx.fill();
        });
        requestAnimationFrame(animateIntroParticles);
    }

    initIntroParticles();
    animateIntroParticles();

    setTimeout(function () {
        document.getElementById('intro-content').classList.remove('opacity-0');
    }, 100);

    setTimeout(function () {
        document.getElementById('intro').classList.add('opacity-0');
        setTimeout(function () {
            document.getElementById('intro').style.display = 'none';
            document.getElementById('main-content').classList.remove('opacity-0');
            setTimeout(runChecks, 1000);
        }, 700);
    }, 8000);

    var steps = [
        { id: "aws", status: "Validando credenciais AWS...", progress: 20 },
        { id: "onedrive", status: "Verificando acesso OneDrive...", progress: 40 },
        { id: "user", status: "Identificando usuário...", progress: 60 },
        { id: "kb", status: "Carregando base de conhecimento...", progress: 80 },
        { id: "ai", status: "Inicializando motores de IA...", progress: 100 }
    ];

    var current = 0;

    function atualizarStep(stepId, status, data) {
        var el = document.getElementById(stepId);
        if (!el) return;
        el.classList.remove("running");
        if (status === "ok") {
            el.classList.add("done");
            var extra = data ? " (" + (data.usuario || data.profile || data.colecao || data.provider || "") + ")" : "";
            el.innerHTML = el.dataset.label || stepId + extra;
        } else {
            el.classList.add("fail");
        }
    }

    function runChecks() {
        fetch("http://127.0.0.1:8000/api/checks")
            .then(function (r) { return r.json(); })
            .then(function (results) {
                results.forEach(function (check) {
                    atualizarStep(check.id, check.status, check.data);
                });
                document.getElementById("status").innerHTML = "Sistema pronto.";
                try { pywebview.api.splash_done(); } catch (e) { }
            })
            .catch(function (err) {
                console.error("Checks error:", err);
                document.getElementById("status").innerHTML = "Erro nas verificacoes, carregando fallback...";
                try { pywebview.api.splash_done(); } catch (e) { }
            });
    }

    function nextStep() {
        if (current >= steps.length) return;
        var step = steps[current];
        document.getElementById("status").innerHTML = step.status;
        var el = document.getElementById(step.id);
        if (el) {
            el.dataset.label = el.innerHTML;
            el.classList.add("running");
        }
        document.getElementById("bar").style.width = step.progress + "%";
        current++;
        setTimeout(nextStep, 400);
    }

    nextStep();
})();
