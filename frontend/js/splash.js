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
            setTimeout(nextStep, 1000);
        }, 700);
    }, 8000);

    var steps = [
        { id: "aws", status: "Validando credenciais AWS...", progress: 20, check: function () { return new Promise(function (r) { setTimeout(r, 1500); }); } },
        { id: "onedrive", status: "Verificando acesso OneDrive...", progress: 40, check: function () { return new Promise(function (r) { setTimeout(r, 1500); }); } },
        { id: "user", status: "Identificando usuário...", progress: 60, check: function () { return new Promise(function (r) { setTimeout(r, 1500); }); } },
        { id: "kb", status: "Carregando base de conhecimento...", progress: 80, check: function () { return new Promise(function (r) { setTimeout(r, 1500); }); } },
        { id: "ai", status: "Inicializando motores de IA...", progress: 100, check: function () { return new Promise(function (r) { setTimeout(r, 1500); }); } }
    ];

    var current = 0;

    function nextStep() {
        if (current >= steps.length) {
            document.getElementById("status").innerHTML = "Sistema pronto.";
            try { pywebview.api.splash_done(); } catch (e) { }
            return;
        }

        var step = steps[current];
        document.getElementById("status").innerHTML = step.status;
        document.getElementById(step.id).classList.add("running");
        document.getElementById("bar").style.width = step.progress + "%";

        step.check().then(function () {
            document.getElementById(step.id).classList.remove("running");
            document.getElementById(step.id).classList.add("done");
            current++;
            nextStep();
        });
    }
})();
