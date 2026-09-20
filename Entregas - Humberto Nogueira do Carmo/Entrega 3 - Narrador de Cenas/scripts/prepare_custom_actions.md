# Clipes custom: sitting_down / standing_up

O Kinetics-400 **não tem** classes limpas de “sentar” / “levantar da cadeira”.
Grave clips curtos (2–5 s) com o celular antes da aula.

## Estrutura

```text
data/custom_actions/
  sitting_down/
    sit_001.mp4
    sit_002.mp4
    ...
  standing_up/
    stand_001.mp4
    stand_002.mp4
    ...
```

## Quantidade sugerida
- Mínimo: **15 vídeos** por classe
- Ideal: **25–30** por classe
- Pessoas/ângulos diferentes ajudam a generalizar para a webcam da sala

## Como gravar
1. Webcam ou celular em tripé, enquadrando cadeira + torso.
2. `sitting_down`: em pé → sentar (um movimento por vídeo).
3. `standing_up`: sentado → levantar.
4. Fundo semelhante ao da sala de aula, se possível.
5. Luz estável; evite zoom durante o movimento.

## Depois de gravar

```bash
python scripts/build_frames_dataset.py
python scripts/train_and_export.py --epochs 12
```

Os frames custom entram juntos com o subset Kinetics em `data/frames/`.
