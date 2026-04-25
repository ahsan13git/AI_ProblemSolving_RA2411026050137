let graph = {};
let nodes = [];
let positions = {};
let assignment = {};
let dragging = null;
let canvas, ctx;

function loadProblem() {
    document.getElementById("home").classList.add("hidden");
    document.getElementById("app").classList.remove("hidden");

    graph = {};
    nodes = [];
    positions = {};
    assignment = {};

    canvas = document.getElementById("canvas");
    ctx = canvas.getContext("2d");

    canvas.onmousedown = startDrag;
    canvas.onmousemove = drag;
    canvas.onmouseup = stopDrag;

    setupMapColoring();
    draw();
}

function goHome() {
    document.getElementById("home").classList.remove("hidden");
    document.getElementById("app").classList.add("hidden");
}

function setupMapColoring() {
    document.getElementById("controls").innerHTML = `
        <div class="section">ADD REGION</div>
        <input id="node">
        <button onclick="addNode()">+ Add Region</button>

        <div class="section">ADD ADJACENCY</div>
        <input id="a">
        <input id="b">
        <button onclick="addEdge()">+ Add Edge</button>

        <div class="section">COLORS AVAILABLE</div>
        <label><input type="checkbox" id="red" checked> Red</label><br>
        <label><input type="checkbox" id="green" checked> Green</label><br>
        <label><input type="checkbox" id="blue" checked> Blue</label><br>
        <label><input type="checkbox" id="yellow" checked> Yellow</label>

        <button style="background:#059669" onclick="solveColoring()">▶ SOLVE</button>
    `;
}

function addNode() {
    let n = document.getElementById("node").value.trim();
    if (!n || nodes.includes(n)) return;

    nodes.push(n);
    graph[n] = [];

    let angle = (2 * Math.PI * nodes.length) / 10;
    positions[n] = {
        x: 350 + 150 * Math.cos(angle),
        y: 250 + 150 * Math.sin(angle)
    };

    draw();
}

function addEdge() {
    let a = document.getElementById("a").value;
    let b = document.getElementById("b").value;

    if (!a || !b || a === b) return;

    if (!graph[a]) graph[a] = [];
    if (!graph[b]) graph[b] = [];

    if (!graph[a].includes(b)) graph[a].push(b);
    if (!graph[b].includes(a)) graph[b].push(a);

    draw();
}

function solveColoring() {
    assignment = {};
    let colors = [];
    if (document.getElementById("red").checked) colors.push("red");
    if (document.getElementById("green").checked) colors.push("green");
    if (document.getElementById("blue").checked) colors.push("blue");
    if (document.getElementById("yellow").checked) colors.push("yellow");

    function isValid(node, color) {
        for (let n of graph[node]) {
            if (assignment[n] === color) return false;
        }
        return true;
    }

    function backtrack(i) {
        if (i === nodes.length) return true;
        let node = nodes[i];
        for (let c of colors) {
            if (isValid(node, c)) {
                assignment[node] = c;
                if (backtrack(i + 1)) return true;
                delete assignment[node];
            }
        }
        return false;
    }

    if (backtrack(0)) {
        showOutput(JSON.stringify(assignment, null, 2));
    } else {
        showOutput("No solution");
    }

    draw();
}

function showOutput(text) {
    document.getElementById("output").innerText = text;
}

function draw() {
    if (!canvas) return;

    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let u in graph) {
        for (let v of graph[u]) {
            let p1 = positions[u];
            let p2 = positions[v];
            if (!p1 || !p2) continue;

            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.strokeStyle = "#374151";
            ctx.stroke();
        }
    }

    for (let n of nodes) {
        let p = positions[n];
        if (!p) continue;

        ctx.beginPath();
        ctx.arc(p.x, p.y, 22, 0, 2 * Math.PI);
        ctx.fillStyle = assignment[n] || "#7c3aed";
        ctx.fill();

        ctx.strokeStyle = "#a78bfa";
        ctx.stroke();

        ctx.fillStyle = "white";
        ctx.fillText(n, p.x - 5, p.y + 5);
    }
}

function getMousePos(e) {
    let rect = canvas.getBoundingClientRect();
    return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
    };
}

function startDrag(e) {
    let m = getMousePos(e);
    for (let n of nodes) {
        let p = positions[n];
        let dx = m.x - p.x;
        let dy = m.y - p.y;
        if (Math.sqrt(dx * dx + dy * dy) < 25) {
            dragging = n;
            return;
        }
    }
}

function drag(e) {
    if (!dragging) return;
    let m = getMousePos(e);
    positions[dragging] = { x: m.x, y: m.y };
    draw();
}

function stopDrag() {
    dragging = null;
}
