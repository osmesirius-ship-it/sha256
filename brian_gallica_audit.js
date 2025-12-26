const crypto = require("crypto");
const fs = require("fs");

function normalizeToBytes(str){
  return Buffer.from(
    str.normalize("NFC")
      .replace(/[\u2013\u2014\u2212]/g,'-')
      .replace(/[\u200B\u200C\u200D\uFEFF]/g,'')
      .replace(/\s+/g,' ')
      .trim(),
    "utf8"
  );
}

function hashChain13(canonical){
  let h = crypto.createHash("sha256").update(normalizeToBytes(canonical)).digest();
  const layers = [h];
  for(let i=1;i<13;i++){
    h = crypto.createHash("sha256").update(h).digest();
    layers.push(h);
  }
  return layers.map(b => b.toString("hex"));
}

// Deterministic mapping helpers
function hexToBigInt(hex){ return BigInt("0x" + hex); }

function pickFromLayer(hex, ndocs, npages, textLen){
  const I = hexToBigInt(hex);
  const docIdx = Number(I % BigInt(ndocs));
  const pageIdx = Number((I / BigInt(ndocs)) % BigInt(npages));
  const off = Number((I / BigInt(ndocs*npages)) % BigInt(Math.max(1, textLen)));
  return { docIdx, pageIdx, off };
}

const canonical = "Brian Christopher Perkins - 1975-05-11 Toledo, OH";
const layers = hashChain13(canonical);

fs.writeFileSync("brian_layers.json", JSON.stringify({ canonical, layers }, null, 2));
console.log("Wrote brian_layers.json");
