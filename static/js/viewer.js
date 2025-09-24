// static/js/iview-init.js

document.addEventListener("DOMContentLoaded", function () {
    const img = document.getElementById("nota-img");
    if (!img) return;
  
    // Create inline viewer inside the wrapper
    const viewer = new Viewer(img, {
      inline: true,       // render inside container
      navbar: false,
      title: true,
      movable: true,      // drag to pan
      zoomable: true,     // wheel / pinch to zoom
      rotatable: false,
      scalable: false,
      zoomOnWheel: true,
      minZoomRatio: 0.1,
      maxZoomRatio: 10,
      minHeight: 750,
      // Fit nicely on first render
      viewed() {
        // Start at 1:1 and fit container
        viewer.zoomTo(1);
      },
      // Ensure it renders inside our wrapper (parent of the image)
      container: document.getElementById("iv-wrapper")
    });
  
    // Optional: external buttons
    const zi = document.getElementById("btn-zoom-in");
    const zo = document.getElementById("btn-zoom-out");
    const rs = document.getElementById("btn-reset");
  
    if (zi) zi.onclick = () => viewer.zoom(0.2, true);
    if (zo) zo.onclick = () => viewer.zoom(-0.2, true);
    if (rs) rs.onclick = () => viewer.reset();
  });
  