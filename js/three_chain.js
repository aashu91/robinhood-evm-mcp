/* js/three_chain.js — Robinhood Chain 3D Interactive Telemetry Engine */

(function() {
    'use strict';

    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;

    if (typeof THREE === 'undefined') {
        console.warn('Three.js not loaded, falling back to 2D canvas.');
        init2DFallback(canvas);
        return;
    }

    let scene, camera, renderer;
    let nodesGroup, blocksGroup, particleSystem;
    let mouseX = 0, mouseY = 0;
    let targetX = 0, targetY = 0;
    let windowHalfX = window.innerWidth / 2;
    let windowHalfY = window.innerHeight / 2;

    const blockHistory = [];
    const MAX_VISIBLE_BLOCKS = 12;

    function init() {
        scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x030712, 0.015);

        camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 1000);
        camera.position.z = 180;
        camera.position.y = 20;

        renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Ambient & Directional Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const goldLight = new THREE.PointLight(0xfbbf24, 2, 200);
        goldLight.position.set(50, 50, 50);
        scene.add(goldLight);

        const emeraldLight = new THREE.PointLight(0x00ff88, 2, 200);
        emeraldLight.position.set(-50, -50, 50);
        scene.add(emeraldLight);

        nodesGroup = new THREE.Group();
        blocksGroup = new THREE.Group();
        scene.add(nodesGroup);
        scene.add(blocksGroup);

        buildNodeNetwork();
        buildInitialBlocks();
        buildTransactionParticles();

        window.addEventListener('resize', onWindowResize, false);
        document.addEventListener('mousemove', onMouseMove, false);

        animate();
    }

    function buildNodeNetwork() {
        const nodeGeo = new THREE.IcosahedronGeometry(2.5, 1);
        const nodeMatGold = new THREE.MeshPhongMaterial({
            color: 0xfbbf24,
            emissive: 0xd97706,
            wireframe: true,
            transparent: true,
            opacity: 0.8
        });

        const nodeMatEmerald = new THREE.MeshPhongMaterial({
            color: 0x00ff88,
            emissive: 0x00aa55,
            wireframe: true,
            transparent: true,
            opacity: 0.8
        });

        const nodePositions = [
            [-80, 40, -40], [80, -30, -60], [-100, -50, -30],
            [90, 60, -50], [0, 80, -80], [-40, -80, -50],
            [50, -70, -40], [0, -90, -70]
        ];

        nodePositions.forEach((pos, i) => {
            const mat = i % 2 === 0 ? nodeMatGold : nodeMatEmerald;
            const mesh = new THREE.Mesh(nodeGeo, mat);
            mesh.position.set(pos[0], pos[1], pos[2]);
            nodesGroup.add(mesh);
        });

        // Connection Lines
        const lineMat = new THREE.LineBasicMaterial({
            color: 0x00f0ff,
            transparent: true,
            opacity: 0.2
        });

        const lineGeo = new THREE.BufferGeometry();
        const linePositions = [];

        nodePositions.forEach((p1, i) => {
            nodePositions.forEach((p2, j) => {
                if (i < j && Math.hypot(p1[0]-p2[0], p1[1]-p2[1], p1[2]-p2[2]) < 140) {
                    linePositions.push(...p1, ...p2);
                }
            });
        });

        lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3));
        const lines = new THREE.LineSegments(lineGeo, lineMat);
        nodesGroup.add(lines);
    }

    function buildInitialBlocks() {
        for (let i = 0; i < MAX_VISIBLE_BLOCKS; i++) {
            spawnBlock(i * 22 - 120);
        }
    }

    function spawnBlock(xPos) {
        const blockGeo = new THREE.BoxGeometry(12, 12, 12);
        const edgesGeo = new THREE.EdgesGeometry(blockGeo);

        const isGold = Math.random() > 0.4;
        const mainColor = isGold ? 0xfbbf24 : 0x00ff88;

        const mat = new THREE.MeshPhongMaterial({
            color: 0x0b0f19,
            transparent: true,
            opacity: 0.7,
            shininess: 80
        });

        const edgeMat = new THREE.LineBasicMaterial({
            color: mainColor,
            linewidth: 2,
            transparent: true,
            opacity: 0.85
        });

        const blockMesh = new THREE.Mesh(blockGeo, mat);
        const wireframe = new THREE.LineSegments(edgesGeo, edgeMat);
        blockMesh.add(wireframe);

        blockMesh.position.set(xPos, Math.sin(xPos * 0.05) * 12, (Math.random() - 0.5) * 20);
        blockMesh.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);

        blocksGroup.add(blockMesh);
        blockHistory.push(blockMesh);

        if (blockHistory.length > MAX_VISIBLE_BLOCKS) {
            const old = blockHistory.shift();
            blocksGroup.remove(old);
        }
    }

    function buildTransactionParticles() {
        const particleCount = 240;
        const geo = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);

        const gold = new THREE.Color(0xfbbf24);
        const emerald = new THREE.Color(0x00ff88);

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 350;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 250;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 200;

            const c = Math.random() > 0.5 ? gold : emerald;
            colors[i * 3] = c.r;
            colors[i * 3 + 1] = c.g;
            colors[i * 3 + 2] = c.b;
        }

        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const mat = new THREE.PointsMaterial({
            size: 2.2,
            vertexColors: true,
            transparent: true,
            opacity: 0.75
        });

        particleSystem = new THREE.Points(geo, mat);
        scene.add(particleSystem);
    }

    function onMouseMove(event) {
        mouseX = (event.clientX - windowHalfX) * 0.05;
        mouseY = (event.clientY - windowHalfY) * 0.05;
    }

    function onWindowResize() {
        windowHalfX = window.innerWidth / 2;
        windowHalfY = window.innerHeight / 2;
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }

    function animate() {
        requestAnimationFrame(animate);

        targetX += (mouseX - targetX) * 0.04;
        targetY += (mouseY - targetY) * 0.04;

        camera.position.x = targetX;
        camera.position.y = 20 - targetY;
        camera.lookAt(scene.position);

        // Rotate nodes & blocks
        nodesGroup.rotation.y += 0.002;
        nodesGroup.rotation.x += 0.001;

        blocksGroup.children.forEach((b, i) => {
            b.rotation.x += 0.005;
            b.rotation.y += 0.007;
            b.position.y += Math.sin(Date.now() * 0.002 + i) * 0.08;
        });

        if (particleSystem) {
            const positions = particleSystem.geometry.attributes.position.array;
            for (let i = 0; i < positions.length; i += 3) {
                positions[i] += Math.sin(Date.now() * 0.001 + i) * 0.15;
                positions[i + 1] += 0.2;
                if (positions[i + 1] > 120) positions[i + 1] = -120;
            }
            particleSystem.geometry.attributes.position.needsUpdate = true;
        }

        renderer.render(scene, camera);
    }

    function init2DFallback(cvs) {
        const ctx = cvs.getContext('2d');
        if (!ctx) return;
        function render2D() {
            cvs.width = window.innerWidth;
            cvs.height = window.innerHeight;
            ctx.fillStyle = '#030712';
            ctx.fillRect(0, 0, cvs.width, cvs.height);
        }
        render2D();
        window.addEventListener('resize', render2D);
    }

    window.addEventListener('DOMContentLoaded', init);
})();
