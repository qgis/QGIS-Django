const urlObj = document.querySelector('div#urlView').dataset.url
const urlMtl = document.querySelector('div#urlView').dataset.mtlUrl

import * as THREE from 'https://threejsfundamentals.org/threejs/resources/threejs/r132/build/three.module.js';
import {OrbitControls} from 'https://threejsfundamentals.org/threejs/resources/threejs/r132/examples/jsm/controls/OrbitControls.js';
import {OBJLoader} from 'https://threejsfundamentals.org/threejs/resources/threejs/r132/examples/jsm/loaders/OBJLoader.js';
import {MTLLoader} from 'https://threejsfundamentals.org/threejs/resources/threejs/r132/examples/jsm/loaders/MTLLoader.js';

const view3d = () => {
  const $container = $("div.view-resource");
  $container.children('div').remove();
  $container.append(
    '<div class="container-3dview"><canvas id="c"></canvas></div>'
  )

  main();
}

$(".style-polaroid").on('click', view3d)


function fitCameraToObject( camera, object, offset ) {
  // Taken from https://discourse.threejs.org/t/camera-zoom-to-fit-object/936/21
  offset = offset || 1.5;
  const boundingBox = new THREE.Box3();
  boundingBox.setFromObject(object);

  const center = boundingBox.getCenter(new THREE.Vector3());
  const size = boundingBox.getSize(new THREE.Vector3());

  const startDistance = center.distanceTo(camera.position);
  const endDistance = camera.aspect > 1 ?
      ((size.y / 2) + offset) / Math.abs(Math.tan(camera.fov / 2)) :
      ((size.y / 2) + offset) / Math.abs(Math.tan(camera.fov / 2)) / camera.aspect;
  camera.position.set(
      camera.position.x * endDistance / startDistance,
      camera.position.y * endDistance / startDistance,
      camera.position.z * endDistance / startDistance,
  );
  camera.lookAt(center);
}

async function main() {

  const canvas = document.querySelector('#c');
  const renderer = new THREE.WebGLRenderer({canvas});

  const fov = 45;
  const aspect = 2;  // the canvas default
  const near = 0.1;
  const far = 100;
  const camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
  camera.position.set(0, 10, 20);

  const controls = new OrbitControls(camera, canvas);
  controls.target.set(0, 5, 0);
  controls.update();

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('white');

  {
    const skyColor = 0xB1E1FF;  // light blue
    const groundColor = 0xB97A20;  // brownish orange
    const intensity = 1;
    const light = new THREE.HemisphereLight(skyColor, groundColor, intensity);
    scene.add(light);
  }

  {

    let materials = null;
    const mtlLoader = new MTLLoader();
    try {
      materials = await mtlLoader.loadAsync(urlMtl)
      materials.preload();
    } catch (e) {
      console.error(e);
    }

    const objLoader = new OBJLoader();
    if (materials) {
      objLoader.setMaterials(materials);
    }

    objLoader.loadAsync(urlObj).then(function(object){
      scene.add(object);

      fitCameraToObject(
          camera,
          object,
          10
      )
      stopAnimation();
    });


  }

  function resizeRendererToDisplaySize(renderer) {
    const canvas = renderer.domElement;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const needResize = canvas.width !== width || canvas.height !== height;
    if (needResize) {
      renderer.setSize(width, height, false);
    }
    return needResize;
  }

  function render() {

    if (resizeRendererToDisplaySize(renderer)) {
      const canvas = renderer.domElement;
      camera.aspect = canvas.clientWidth / canvas.clientHeight;
      camera.updateProjectionMatrix();
    }

    renderer.render(scene, camera);

    requestAnimationFrame(render);
  }

  function loadAnimation(){
    $('.container-3dview').append(
      '<div class="loading"></div>'
    )
    console.log('loading')
  }
  function stopAnimation(){
    $('.container-3dview').children('div.loading').remove();
    console.log('remove')
  }

  loadAnimation();
  requestAnimationFrame(render);
}
