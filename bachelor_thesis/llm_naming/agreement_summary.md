# Multi-LLM cluster naming agreement

Models: 11; clusters: 4.

Krippendorff $\alpha$ (nominal, methodology category) = 0.531

## Cosine similarity to expert baseline (cluster name embeddings)

| model                             |     1 |     2 |     3 |     4 |   mean |
|:----------------------------------|------:|------:|------:|------:|-------:|
| anthropic__claude-haiku-4-5       | 0.519 | 0.748 | 0.836 | 0.637 |  0.685 |
| anthropic__claude-opus-4-7        | 0.755 | 0.881 | 0.811 | 0.702 |  0.787 |
| anthropic__claude-sonnet-4-6      | 0.924 | 0.9   | 0.812 | 0.858 |  0.874 |
| deepseek__deepseek-v4-flash_cloud | 0.238 | 0.797 | 0.853 | 0.72  |  0.652 |
| deepseek__deepseek-v4-pro_cloud   | 0.152 | 0.862 | 0.292 | 0.754 |  0.515 |
| google__gemma4_31b-cloud          | 0.216 | 0.879 | 0.725 | 0.825 |  0.661 |
| minimax__minimax-m2.7_cloud       | 0.537 | 0.716 | 0.771 | 0.741 |  0.691 |
| moonshot__kimi-k2.6_cloud         | 0.574 | 0.58  | 0.834 | 0.688 |  0.669 |
| qwen__qwen3-coder-next_cloud      | 0.315 | 0.779 | 0.832 | 0.383 |  0.577 |
| qwen__qwen3.5_397b-cloud          | 0.243 | 0.733 | 0.857 | 0.484 |  0.579 |
| zhipu__glm-5.1_cloud              | 0.599 | 0.797 | 0.879 | 0.821 |  0.774 |

## Schools Jaccard vs expert

| model                             |     1 |   2 |     3 |     4 |   mean |
|:----------------------------------|------:|----:|------:|------:|-------:|
| anthropic__claude-haiku-4-5       | 0.25  | 0   | 0.333 | 0.5   |  0.271 |
| anthropic__claude-opus-4-7        | 0.333 | 0.2 | 0.667 | 0.5   |  0.425 |
| anthropic__claude-sonnet-4-6      | 0.625 | 0.5 | 0.667 | 0.5   |  0.573 |
| deepseek__deepseek-v4-flash_cloud | 0.333 | 0   | 0.111 | 0     |  0.111 |
| deepseek__deepseek-v4-pro_cloud   | 0.333 | 0   | 0     | 0.2   |  0.133 |
| google__gemma4_31b-cloud          | 0.5   | 0   | 0     | 0     |  0.125 |
| minimax__minimax-m2.7_cloud       | 0.25  | 0   | 0     | 0     |  0.062 |
| moonshot__kimi-k2.6_cloud         | 0.143 | 0   | 0.125 | 0     |  0.067 |
| qwen__qwen3-coder-next_cloud      | 0.571 | 0   | 0     | 0     |  0.143 |
| qwen__qwen3.5_397b-cloud          | 0.286 | 0   | 0     | 0.167 |  0.113 |
| zhipu__glm-5.1_cloud              | 0.4   | 0   | 0.167 | 0.125 |  0.173 |

## Per-cluster modal-method agreement

- Cluster 1: 0.91
- Cluster 2: 1.00
- Cluster 3: 0.55
- Cluster 4: 0.64