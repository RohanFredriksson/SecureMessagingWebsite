/*
 - Generates a public and private key pair for asymmetric encryption.
*/
async function generateKeyPair() {
  const pair = await window.crypto.subtle.generateKey({name: "ECDH", namedCurve: "P-256"}, true, ["deriveKey", "deriveBits"]);
  const publicWebKey = await window.crypto.subtle.exportKey("jwk", pair.publicKey);
  const privateWebKey = await window.crypto.subtle.exportKey("jwk", pair.privateKey);
  return {"public": publicWebKey, "private": privateWebKey};
};

/*
 - Uses Elliptic Curve Diffie Hellman to generate a shared secret master key between two parties.
*/
async function generateSecret(publicWebKey, privateWebKey) {
  const public = await window.crypto.subtle.importKey("jwk", publicWebKey, {name: "ECDH", namedCurve: "P-256"}, true, []);
  const private = await window.crypto.subtle.importKey("jwk", privateWebKey, {name: "ECDH", namedCurve: "P-256",}, true, ["deriveKey", "deriveBits"]);
  const secret = await window.crypto.subtle.deriveKey({name: "ECDH", public: public}, private, {name: "AES-GCM", length: 256}, true, ["encrypt", "decrypt"]);
  const secretWebKey = await window.crypto.subtle.exportKey("jwk", secret);
  return secretWebKey;
}

/*
 - Uses a shared master secret to symmetrically encrypt the text.
 - Uses "independent" keys on enc-then-mac encryption with AES-GCM.
 - Returns encryped data, a HMAC, and an initialisation vector.
*/
async function encrypt(text, secretWebKey) {
    
  // Import the key.
  const secret = await window.crypto.subtle.importKey("jwk", secretWebKey, {name: "AES-GCM", length: 256}, true, ["encrypt", "decrypt"]);

  // Compute the data encryption.
  const vector = window.crypto.getRandomValues(new Uint8Array(12))
  const encodedText = new TextEncoder().encode(text);
  const encryptedData = await window.crypto.subtle.encrypt({name: "AES-GCM", iv: new TextEncoder().encode(vector)}, secret, encodedText);
  let buffer = new Uint8Array(encryptedData);
  let string = String.fromCharCode.apply(null, buffer);
  const data = btoa(string);
  
  // Compute the HMAC on the data
  const digest = hash(secretWebKey.k);
  const sign = await window.crypto.subtle.sign(
    "HMAC",
    await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode(digest),
      { name: "HMAC", hash: "SHA-256"},
      false,
      ["sign", "verify"]
    ),
    new TextEncoder().encode(data)
  );
  buffer = new Uint8Array(sign);
  string = String.fromCharCode.apply(null, buffer);
  const hmac = btoa(string)

  return {data: data, hmac: hmac, vector: btoa(String.fromCharCode.apply(null, vector))};
}

/*
 - Uses a shared master secret to symmetrically decrypt the cipher.
 - Verifies the HMAC, and if it is verified, then the message is decrypted.
 - Returns a verification status, and a message if verified.
*/
async function decrypt(cipher, secretWebKey) {

  // Import the key
  const secret = await window.crypto.subtle.importKey("jwk", secretWebKey, {name: "AES-GCM", length: 256}, true, ["encrypt", "decrypt"]);

  // This should be in the try block, because if someone tampers with the cipher, it will throw an exception when trying to decode.
  try {

    // Verify the HMAC
    const digest = hash(secretWebKey.k);
    let string = atob(cipher.hmac);
    let buffer = new Uint8Array([...string].map((char) => char.charCodeAt(0)));
    const result = await crypto.subtle.verify(
      "HMAC",
      await crypto.subtle.importKey(
        "raw",
        new TextEncoder().encode(digest),
        { name: "HMAC", hash: "SHA-256"},
        false,
        ["sign", "verify"]
      ),
      buffer,
      new TextEncoder().encode(cipher.data)
    ); 

    if (!result) {
      return {verified: false, message: null};
    }

    // Decrypt the data
    string = atob(cipher.data);
    buffer = new Uint8Array([...string].map((char) => char.charCodeAt(0)));
    const algorithm = {name: "AES-GCM", iv: new TextEncoder().encode(new Uint8Array([...atob(cipher.vector)].map((char) => char.charCodeAt(0))))};
    const decryptedData = await window.crypto.subtle.decrypt(algorithm, secret, buffer);
    return {verified: true, message: new TextDecoder().decode(decryptedData)};

  } catch (err) {
    return {verified: false, message: null};
  }
}

async function hash(message) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(message));
  const buffer = new Uint8Array(digest);
  const string = String.fromCharCode.apply(null, buffer);
  const data = btoa(message);
  return data;
}

function validatePublicKeyString(string) {

  // If there is no string, return false.
  if (string == null) {return false;}

  // Try to parse into a JSON object.
  try {
    public = JSON.parse(string);
  
    // Check if all necessary keys are in the object.
    if (!public.hasOwnProperty("crv")) {return false;}
    if (!public.hasOwnProperty("ext")) {return false;}
    if (!public.hasOwnProperty("key_ops")) {return false;}
    if (!public.hasOwnProperty("kty")) {return false;}
    if (!public.hasOwnProperty("x")) {return false;}
    if (!public.hasOwnProperty("y")) {return false;}

    // Check all the properties of each string.
    if (public.crv != "P-256") {return false;}
    if (public.ext != true) {return false;}
    if (public.key_ops.length != 0) {return false;}
    if (public.kty != "EC") {return false;}

    return true;
  
  } catch (err) {return false;}

  
}

function validatePrivateKeyString(string) {

  // If there is no string, return false.
  if (string == null) {return false;}

  // Try to parse into a JSON object.
  try {
    private = JSON.parse(string);

    // Check if all necessary keys are in the object.
    if (!private.hasOwnProperty("crv")) {return false;}
    if (!private.hasOwnProperty("d")) {return false;}
    if (!private.hasOwnProperty("ext")) {return false;}
    if (!private.hasOwnProperty("key_ops")) {return false;}
    if (!private.hasOwnProperty("kty")) {return false;}
    if (!private.hasOwnProperty("x")) {return false;}
    if (!private.hasOwnProperty("y")) {return false;}

    // Check all the properties of each string.
    if (private.crv != "P-256") {return false;}
    if (private.ext != true) {return false;}
    if (private.key_ops.length != 2) {return false;}
    if (private.key_ops[0] != "deriveKey" && private.key_ops[1] != "deriveBits") {return false;}
    if (private.kty != "EC") {return false;}
    
    return true;

  } catch (err) {return false;}

}

async function main() {

  alice = await generateKeyPair();
  bob = await generateKeyPair();
  mallory = await generateKeyPair();

  aliceSecret = await generateSecret(bob.public, alice.private);
  bobSecret = await generateSecret(alice.public, bob.private);
  mallorySecret = await generateSecret(alice.public, mallory.private);

  cipher = await encrypt("According to all known laws of aviation, there is no way a bee should be able to fly. Its wings are too small to get its fat little body off the ground. The bee, of course, flies anyway because bees don't care what humans think is impossible.", aliceSecret);

  data = await decrypt(cipher, bobSecret);
  console.log(data);

  data = await decrypt(cipher, mallorySecret);
  console.log(data);

}
main();