class FaceClass:
  def __init__(face, pokemonName, releaseDate, rarity, sleepFaceName, energy, ID, np, expCandy, researchExp, dreamShard):
    face.pokemonName = pokemonName
    face.releaseDate = releaseDate
    face.rarity = rarity
    face.sleepFaceName = sleepFaceName
    face.energy = energy
    face.ID = ID
    face.np = np
    face.expCandy = expCandy
    face.researchExp = researchExp
    face.dreamShard = dreamShard
  def to_dict(face):
    return {
      "pokemonName": face.pokemonName,
      "releaseDate": face.releaseDate,
      "rarity": face.rarity,
      "sleepFaceName": face.sleepFaceName,
      "energy": face.energy,
      "ID": face.ID,
      "np": face.np,
      "expCandy": face.expCandy,
      "researchExp": face.researchExp,
      "dreamShard": face.dreamShard,
    }
  @staticmethod 
  def compare(a, b):
    # 優先度: np > エナジー > 寝顔ID
    if a.np != b.np:
      return a.np - b.np
    if a.energy != b.energy:
      return a.energy - b.energy
    if a.ID != b.ID:
      return a.ID - b.ID
    return 0  # 3条件が同一の場合

class FaceClassNotDecided:
  def __init__(face, pokemonName, rarity, sleepFaceName, np):
    face.pokemonName = pokemonName
    face.rarity = rarity
    face.sleepFaceName = sleepFaceName
    face.np = np
  def to_dict(face):
    return {
      "pokemonName": face.pokemonName,
      "rarity": face.rarity,
      "sleepFaceName": face.sleepFaceName,
      "np": face.np,
    }

class FaceClassError:
  def __init__(face, pokemonName, rarity, sleepFaceName):
    face.pokemonName = pokemonName
    face.rarity = rarity
    face.sleepFaceName = sleepFaceName
  def to_dict(face):
    return {
      "pokemonName": face.pokemonName,
      "rarity": face.rarity,
      "sleepFaceName": face.sleepFaceName
    }