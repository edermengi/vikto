## Game state diagram

```mermaid
stateDiagram-v2
    state if_state <<choice>>
    [*] --> WAIT_START
    WAIT_START --> ASK_TOPIC: All players  click 'START GAME'
    ASK_TOPIC --> ASK_QUESTION: Players select topic
    ASK_QUESTION --> SHOW_ANSWER: Players select answer
    SHOW_ANSWER --> if_state
    if_state --> SHOW_WINNER: if n == 0
    if_state --> ASK_TOPIC : if n > 0
    SHOW_WINNER --> [*]
    
```

## User Journey

```mermaid
journey
    title Play game
    section Login
      Type name: 3: Me
      Choose avatar: 3: Me
    section New Game
      Invite friends: 5: Me
      Other players join: 5: Friends
      Wait friends ready: 5: Me,Friends
      Select theme: 5: Me, Friends
      Answer quizes: 6: Me, Friends
```

## Storage

```mermaid
classDiagram
    direction RL
    GameDetails .. GameUserDetails : GameId
    GameDetails .. Answers : GameId
    class GameDetails{
      GameId
      Status [Active|Finished]
      StartTime
      FinishTime
      Winner      
    }
    class Answers{
      GameId
      UserId
      AnswerTime
      Correct [Yes|No]      
    }
    class GameUserDetails{
      UserId
      Score
    }
```

### Game table

#### Game details

| GameId | Entity        | StartTime        | FinishTime       | Round |
|--------|---------------|------------------|------------------|-------|
| 1321   | `GAME#ACTIVE` | 2022-10-11T11:02 | 2022-10-11T22:04 | 1     |

#### Game round details

| GameId | Entity        | StartTime        | FinishTime       | Round |
|--------|---------------|------------------|------------------|-------|
| 1321   | `GAME#ACTIVE` | 2022-10-11T11:02 | 2022-10-11T22:04 | 1     |

#### Game history

| GameId | Entity    | StartTime        | FinishTime       | Round |
|--------|-----------|------------------|------------------|-------|
| 1321   | `ROUND#1` | 2022-10-11T11:02 | 2022-10-11T22:04 | 1     |

#### GameUserDetails - user details in game

| GameId | Entity | UserId | Start time       | Score |
|--------|--------|--------|------------------|-------|
| 1321   | `USER` | 323    | 2022-10-11T11:02 | 4.2   |
| 1321   | `USER` | 453    | 2022-10-11T11:02 | 2.0   |
| 1321   | `USER` | 22     | 2022-10-11T11:02 | 7.9   |
