const map = document.querySelector(".hecs-map");
const activeCard = document.querySelector(".hecs-hex.is-active");

if (map && activeCard) {
  const mapBox = map.getBoundingClientRect();
  const activeBox = activeCard.getBoundingClientRect();
  map.scrollLeft += activeBox.left - mapBox.left - mapBox.width / 2 + activeBox.width / 2;
}
